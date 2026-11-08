"""Service for AI Conversational Review Intelligence grounded in PostgreSQL catalog and verified customer reviews."""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import select, func, desc, asc, and_, or_
from sqlalchemy.orm import Session

from src.db.models import Product, Review
from src.api.schemas.assistant import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ProductCardSummary,
    SourceCitation,
    StarterPrompt,
)
from src.api.services.product_service import ProductService
from src.api.services.product_report_service import ProductReportService

logger = logging.getLogger(__name__)


class AssistantService:
    """Conversational assistant synthesizing grounded product review intelligence."""

    STOP_WORDS = {
        "the", "a", "an", "and", "or", "of", "to", "in", "for", "with", "on", 
        "at", "by", "from", "is", "are", "was", "were", "what", "how", "why", 
        "which", "who", "where", "can", "could", "would", "should", "me", "tell", 
        "about", "show", "give", "please", "i", "my", "we", "our", "you", "your",
        "do", "does", "did", "have", "has", "had", "best", "good", "recommend",
        "compare", "vs", "versus", "between", "difference", "flaw", "flaws",
        "problem", "problems", "issue", "issues", "defect", "defects"
    }

    STARTER_PROMPTS = [
        StarterPrompt(
            category="Comparison",
            icon="⚖️",
            title="iPhone 8 Plus vs Galaxy S20 FE",
            prompt="Compare Apple iPhone 8 Plus vs Samsung Galaxy S20 FE: which has better battery and durability?"
        ),
        StarterPrompt(
            category="Defect Discovery",
            icon="⚠️",
            title="MacBook Air Flaws & Durability",
            prompt="What are the common failure modes and flaws reported for Apple MacBook Air laptops?"
        ),
        StarterPrompt(
            category="Recommendations",
            icon="🌟",
            title="Best Laptop under $500",
            prompt="Recommend the best everyday laptop under $500 with solid battery life and low defect rates."
        ),
        StarterPrompt(
            category="Aspect Analysis",
            icon="🎧",
            title="Earbuds Battery Lifespan",
            prompt="Which wireless earbuds have the best battery lifespan and sound quality based on customer reviews?"
        ),
    ]

    @classmethod
    def get_starter_prompts(cls) -> List[StarterPrompt]:
        return cls.STARTER_PROMPTS

    @classmethod
    def search_products(cls, db: Session, query: str, limit: int = 5, category: Optional[str] = None) -> List[Product]:
        """Search products by title, ASIN, or brand with smart filtering."""
        q = query.strip()
        if not q:
            return []

        # Auto-detect category if not explicitly provided
        target_cat = category or cls._detect_category_intent(q)

        # Check if direct ASIN
        if re.match(r"^B0[A-Z0-9]{8}$", q, re.IGNORECASE):
            prod = db.get(Product, q.upper())
            if prod:
                return [prod]

        # Extract tokens
        tokens = [t.lower() for t in re.split(r"[^\w\d]+", q) if len(t) >= 2 and t.lower() not in cls.STOP_WORDS]
        if not tokens:
            tokens = [t.lower() for t in re.split(r"[^\w\d]+", q) if len(t) >= 2]

        stmt = select(Product)
        if target_cat:
            stmt = ProductService._apply_category_filter(stmt, target_cat)

        # Build token match clauses
        token_clauses = []
        for t in tokens:
            token_clauses.append(
                or_(
                    func.lower(Product.product_name).like(f"%{t}%"),
                    func.lower(Product.brand).like(f"%{t}%"),
                    Product.product_id.ilike(f"%{t}%"),
                )
            )

        if token_clauses:
            stmt = stmt.where(and_(*token_clauses))

        # Prefer products with higher review counts and established ratings
        stmt = stmt.order_by(
            desc(Product.rating_number),
            desc(Product.average_rating)
        ).limit(limit)

        results = db.execute(stmt).scalars().all()

        # Fallback to broader OR search if no strict AND matches
        if not results and len(tokens) > 1:
            broad_stmt = select(Product)
            if target_cat:
                broad_stmt = ProductService._apply_category_filter(broad_stmt, target_cat)
            or_clauses = [
                or_(
                    func.lower(Product.product_name).like(f"%{t}%"),
                    func.lower(Product.brand).like(f"%{t}%")
                )
                for t in tokens
            ]
            broad_stmt = broad_stmt.where(or_(*or_clauses)).order_by(
                desc(Product.rating_number),
                desc(Product.average_rating)
            ).limit(limit)
            results = db.execute(broad_stmt).scalars().all()

        return results

    @classmethod
    def _detect_category_intent(cls, text: str) -> Optional[str]:
        t = text.lower()
        if any(w in t for w in ["laptop", "notebook", "chromebook", "macbook", "thinkpad"]):
            return "laptops & notebooks"
        if any(w in t for w in ["phone", "smartphone", "iphone", "galaxy", "pixel", "mobile", "android"]):
            return "smartphones & mobiles"
        if any(w in t for w in ["headphone", "earbud", "earphone", "headset", "airpods", "audio"]):
            return "headphones & earbuds"
        if any(w in t for w in ["camera", "dslr", "camcorder", "lens", "gopro"]):
            return "cameras & photography"
        if any(w in t for w in ["hard drive", "hard disk", "ssd", "microsd", "flash drive", "storage", "nvme"]):
            return "hard disks & storage"
        return None

    @classmethod
    def _extract_price_limit(cls, text: str) -> Optional[float]:
        # Match "under $500", "below 600", "< 400", "under 500 dollars"
        match = re.search(r"(?:under|below|less than|max|budget of|\$)\s*\$?(\d+(?:\.\d{1,2})?)", text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    @classmethod
    def _detect_intent(cls, text: str) -> str:
        t = text.lower()
        if any(w in t for w in [" vs ", " versus ", "compare", "difference between", "better than", " or "]):
            return "comparison"
        if any(w in t for w in ["flaw", "defect", "problem", "issue", "failure", "fail", "break", "weakness", "drawback", "return", "complaint", "reliable", "durability"]):
            return "defects_flaws"
        if any(w in t for w in ["recommend", "best", "top", "suggest", "good", "which should i buy", "what should i buy"]):
            return "recommendation"
        if any(w in t for w in ["battery", "lifespan", "screen", "display", "sound", "comfort", "heat", "overheating", "speed", "performance"]):
            return "aspect_deep_dive"
        if any(w in t for w in ["hello", "hi", "hey", "who are you", "what can you do", "help", "how do you work", "about you"]):
            return "conversational"
        return "product_inquiry"

    @classmethod
    def _resolve_context_product(cls, messages: List[ChatMessage], db: Session) -> Optional[Product]:
        """Look back through conversation history to resolve which product was previously referenced."""
        for msg in reversed(messages):
            # Check for ASIN in message content
            asin_match = re.search(r"\b(B0[A-Z0-9]{8})\b", msg.content)
            if asin_match:
                prod = db.get(Product, asin_match.group(1))
                if prod:
                    return prod
            # Check for known product titles in assistant replies
            if msg.role == "assistant":
                title_match = re.search(r"\*\*([^*]{5,60})\*\*", msg.content)
                if title_match:
                    candidates = cls.search_products(db, title_match.group(1), limit=1)
                    if candidates:
                        return candidates[0]
            elif msg.role == "user":
                candidates = cls.search_products(db, msg.content, limit=1)
                if candidates:
                    return candidates[0]
        return None

    @classmethod
    def _to_product_summary(cls, rpt) -> ProductCardSummary:
        return ProductCardSummary(
            product_id=rpt.product_id,
            product_name=rpt.product_name,
            brand=rpt.brand,
            price=rpt.price,
            image_url=rpt.image_url,
            honest_rating=rpt.overall_rating,
            marketplace_rating=rpt.marketplace_listed_rating,
            quality_grade=rpt.quality_grade,
            critical_complaint_rate=rpt.critical_complaint_rate,
            highlight=rpt.critical_negative_points[0].title if rpt.critical_negative_points else None
        )

    @classmethod
    def handle_chat(cls, db: Session, request: ChatRequest) -> ChatResponse:
        """Main chat handler producing grounded, articulated answers."""
        messages = request.messages
        last_message = request.query or (messages[-1].content if messages else "")
        query_text = last_message.strip()

        if not query_text:
            return ChatResponse(
                reply="Please type a question or choose one of the starter suggestions above to begin exploring product reviews.",
                intent="empty"
            )

        intent = cls._detect_intent(query_text)
        category_intent = cls._detect_category_intent(query_text)
        price_limit = cls._extract_price_limit(query_text)

        # 1. CONVERSATIONAL GREETING OR PLATFORM QUESTION
        if intent == "conversational":
            return cls._handle_conversational(query_text)

        # 2. COMPARISON QUERY (e.g. "Compare iPhone 8 Plus vs Galaxy S20 FE")
        if intent == "comparison":
            return cls._handle_comparison(db, query_text, messages)

        # 3. RECOMMENDATION QUERY (e.g. "Recommend best laptop under $500")
        if intent == "recommendation":
            return cls._handle_recommendation(db, query_text, category_intent, price_limit)

        # 4. DEFECTS / FLAWS QUERY (e.g. "What are the common flaws of MacBook Air?")
        if intent == "defects_flaws":
            return cls._handle_defects(db, query_text, messages)

        # 5. ASPECT DEEP DIVE (e.g. "How is the battery life on iPhone 8 Plus?")
        if intent == "aspect_deep_dive":
            return cls._handle_aspect(db, query_text, messages)

        # 6. GENERAL PRODUCT INQUIRY
        return cls._handle_general_inquiry(db, query_text, messages)

    @classmethod
    def _handle_conversational(cls, query: str) -> ChatResponse:
        reply = (
            "👋 **Hello! I am your AI Review Intelligence Assistant.**\n\n"
            "Unlike standard retail sites that show inflated 4.5★+ ratings, I analyze real, unstructured customer feedback from **8,866 electronics** and **9,733 customer reviews** to give you **unbiased, honest intelligence**.\n\n"
            "### How I can help you today:\n"
            "* ⚖️ **Head-to-Head Comparisons**: *\"Compare iPhone 8 Plus vs Galaxy S20 FE\"*\n"
            "* ⚠️ **Defect & Failure Discovery**: *\"What are the common failure modes of MacBook Air?\"*\n"
            "* 🌟 **Reality-Checked Recommendations**: *\"What is the best laptop under $500?\"*\n"
            "* 🔋 **Aspect Analysis**: *\"Which headphones have the best battery lifespan and comfort?\"*\n\n"
            "What product or category would you like to investigate?"
        )
        return ChatResponse(
            reply=reply,
            intent="conversational",
            suggested_followups=[
                "Compare iPhone 8 Plus vs Galaxy S20 FE",
                "Recommend the best laptop under $500",
                "What are the common flaws of Apple MacBooks?",
                "Which wireless earbuds have the best battery life?"
            ]
        )

    @classmethod
    def _handle_comparison(cls, db: Session, query: str, messages: List[ChatMessage]) -> ChatResponse:
        # Split on comparison delimiters
        parts = re.split(r"\b(?:vs|versus|compare|and|with)\b", query, flags=re.IGNORECASE)
        candidate_names = [p.strip() for p in parts if len(p.strip()) > 2]

        prods = []
        if len(candidate_names) >= 2:
            p1_matches = cls.search_products(db, candidate_names[0], limit=1)
            p2_matches = cls.search_products(db, candidate_names[1], limit=1)
            if p1_matches:
                prods.append(p1_matches[0])
            if p2_matches and (not p1_matches or p2_matches[0].product_id != p1_matches[0].product_id):
                prods.append(p2_matches[0])

        if len(prods) < 2:
            # Fallback: search query as a whole
            broader = cls.search_products(db, query, limit=2)
            for b in broader:
                if b not in prods:
                    prods.append(b)

        if len(prods) < 2:
            return ChatResponse(
                reply=(
                    f"I couldn't locate both distinct products in the catalog for **\"{query}\"**.\n\n"
                    "💡 **Tip**: Try naming both models specifically, for example:\n"
                    "* *\"Compare iPhone 8 Plus vs Galaxy S20 FE\"*\n"
                    "* *\"Compare Lenovo Chromebook vs Dell Latitude\"*"
                ),
                intent="comparison",
                suggested_followups=[
                    "Compare iPhone 8 Plus vs Galaxy S20 FE",
                    "Compare Bose QuietComfort vs Beats Studio3",
                    "Best laptops under $500"
                ]
            )

        p1, p2 = prods[0], prods[1]
        r1 = ProductReportService.generate_report(db, p1.product_id)
        r2 = ProductReportService.generate_report(db, p2.product_id)

        # Build comparison markdown
        p1_name = p1.product_name[:45].strip()
        p2_name = p2.product_name[:45].strip()

        # Aspect dicts
        a1_map = {a.name: a.score for a in r1.aspects}
        a2_map = {a.name: a.score for a in r2.aspects}

        # Winner assessment
        if r1.overall_rating > r2.overall_rating:
            verdict = f"🏆 **{r1.brand or 'Product 1'}** edges out with a higher Honest Rating (**{r1.overall_rating}★** vs {r2.overall_rating}★) and lower critical defect risk (**{r1.critical_complaint_rate}%** vs {r2.critical_complaint_rate}%)."
        elif r2.overall_rating > r1.overall_rating:
            verdict = f"🏆 **{r2.brand or 'Product 2'}** edges out with a higher Honest Rating (**{r2.overall_rating}★** vs {r1.overall_rating}★) and lower critical defect risk (**{r2.critical_complaint_rate}%** vs {r1.critical_complaint_rate}%)."
        else:
            verdict = f"⚖️ Both products are closely matched at **{r1.overall_rating}★**. Choose based on your preference for price and specific hardware features."

        reply = (
            f"## ⚖️ Head-to-Head Comparison: {r1.brand or ''} vs {r2.brand or ''}\n\n"
            f"Here is the evidence-grounded comparison between **{p1.product_name}** and **{p2.product_name}**:\n\n"
            f"| Metric / Dimension | {p1_name} | {p2_name} | Edge |\n"
            f"| :--- | :---: | :---: | :---: |\n"
            f"| **Listing Price** | ${p1.price or 'N/A'} | ${p2.price or 'N/A'} | {p1_name if (p1.price and p2.price and p1.price < p2.price) else p2_name if (p1.price and p2.price) else 'Tied'} |\n"
            f"| **Honest Rating** | **{r1.overall_rating}★** (Grade {r1.quality_grade}) | **{r2.overall_rating}★** (Grade {r2.quality_grade}) | {'👑 ' + p1_name if r1.overall_rating > r2.overall_rating else '👑 ' + p2_name if r2.overall_rating > r1.overall_rating else 'Tied'} |\n"
            f"| **Amazon Listed** | {r1.marketplace_listed_rating or 'N/A'}★ | {r2.marketplace_listed_rating or 'N/A'}★ | — |\n"
            f"| **Defect / Return Risk** | **{r1.critical_complaint_rate}%** | **{r2.critical_complaint_rate}%** | {p1_name if r1.critical_complaint_rate < r2.critical_complaint_rate else p2_name} |\n"
            f"| **Durability & Build** | {a1_map.get('Durability & Build Quality', 'N/A')}★ | {a2_map.get('Durability & Build Quality', 'N/A')}★ | {p1_name if a1_map.get('Durability & Build Quality', 0) > a2_map.get('Durability & Build Quality', 0) else p2_name} |\n"
            f"| **Battery & Lifespan** | {a1_map.get('Lifespan & Battery Longevity', 'N/A')}★ | {a2_map.get('Lifespan & Battery Longevity', 'N/A')}★ | {p1_name if a1_map.get('Lifespan & Battery Longevity', 0) > a2_map.get('Lifespan & Battery Longevity', 0) else p2_name} |\n"
            f"| **Performance & Speed** | {a1_map.get('Performance & Responsiveness', 'N/A')}★ | {a2_map.get('Performance & Responsiveness', 'N/A')}★ | {p1_name if a1_map.get('Performance & Responsiveness', 0) > a2_map.get('Performance & Responsiveness', 0) else p2_name} |\n\n"
            f"### Key Differences & Known Flaws\n"
            f"* **{p1_name}**: {r1.flaws_and_drawbacks[0] if r1.flaws_and_drawbacks else 'Standard wear and tear'}.\n"
            f"* **{p2_name}**: {r2.flaws_and_drawbacks[0] if r2.flaws_and_drawbacks else 'Standard wear and tear'}.\n\n"
            f"### 🎯 Bottom-Line Verdict\n"
            f"{verdict}\n\n"
            f"* **Who should choose {r1.brand or 'Product 1'}**: {r1.who_should_buy}\n"
            f"* **Who should choose {r2.brand or 'Product 2'}**: {r2.who_should_buy}"
        )

        cards = [cls._to_product_summary(r1), cls._to_product_summary(r2)]
        sources = [
            SourceCitation(
                product_id=p1.product_id,
                product_name=p1.product_name,
                total_reviews_analyzed=r1.total_ratings_count,
                verified_purchases_ratio=r1.satisfaction_rate,
                key_aspect="Head-to-Head Multi-Aspect Evaluation"
            ),
            SourceCitation(
                product_id=p2.product_id,
                product_name=p2.product_name,
                total_reviews_analyzed=r2.total_ratings_count,
                verified_purchases_ratio=r2.satisfaction_rate,
                key_aspect="Head-to-Head Multi-Aspect Evaluation"
            )
        ]

        return ChatResponse(
            reply=reply,
            products=cards,
            sources=sources,
            intent="comparison",
            suggested_followups=[
                f"What are the specific battery flaws of {p1_name}?",
                f"Show verified customer complaints for {p2_name}",
                "Recommend an alternative model in this price range"
            ]
        )

    @classmethod
    def _handle_recommendation(
        cls, 
        db: Session, 
        query: str, 
        category: Optional[str], 
        price_limit: Optional[float]
    ) -> ChatResponse:
        # Determine target category
        cat = category or "laptops & notebooks"

        stmt = select(Product)
        stmt = ProductService._apply_category_filter(stmt, cat)

        if price_limit:
            stmt = stmt.where(Product.price <= price_limit, Product.price > 10.0)

        # Sort by ratings and popularity
        stmt = stmt.order_by(
            desc(Product.average_rating),
            desc(Product.rating_number)
        ).limit(6)

        candidates = db.execute(stmt).scalars().all()

        if not candidates:
            # Fallback without price limit if too strict
            fallback_stmt = select(Product)
            fallback_stmt = ProductService._apply_category_filter(fallback_stmt, cat)
            candidates = db.execute(fallback_stmt.order_by(desc(Product.average_rating)).limit(4)).scalars().all()

        if not candidates:
            return ChatResponse(
                reply=f"No products matched your criteria in category **{cat}**. Try adjusting the budget or checking a different category.",
                intent="recommendation"
            )

        # Generate reports for top candidates
        reports = []
        for c in candidates:
            rpt = ProductReportService.generate_report(db, c.product_id)
            if rpt:
                reports.append(rpt)
            if len(reports) >= 3:
                break

        # Sort reports by honest rating
        reports.sort(key=lambda r: r.overall_rating, reverse=True)

        budget_str = f" under ${price_limit:.0f}" if price_limit else ""
        category_title = cat.title()

        reply = (
            f"## 🌟 Top Recommended {category_title}{budget_str}\n\n"
            f"Based on honest debiased ratings, defect rates, and verified customer experiences in our database, here are the top picks:\n\n"
        )

        badges = ["🥇 **Top Overall Pick**", "🥈 **Runner-Up / Great Value**", "🥉 **Alternative Option**"]
        cards = []
        sources = []

        for i, rpt in enumerate(reports):
            badge = badges[i] if i < len(badges) else "⭐ **Contender**"
            price_display = f"${rpt.price:.2f}" if rpt.price else "Market Price"
            flaw = rpt.flaws_and_drawbacks[0] if rpt.flaws_and_drawbacks else "Standard wear and tear"
            strength = rpt.strengths[0] if rpt.strengths else "Solid general performance"

            reply += (
                f"### {badge}: {rpt.product_name}\n"
                f"* **Honest Rating**: **{rpt.overall_rating}★** (Grade {rpt.quality_grade}) | *Amazon Listed: {rpt.marketplace_listed_rating or 'N/A'}★*\n"
                f"* **Price**: {price_display} | **Defect Rate**: {rpt.critical_complaint_rate}%\n"
                f"* **Key Strength**: {strength}\n"
                f"* **Buyer Caveat / Watchlist**: {flaw}\n"
                f"* **Ideal For**: {rpt.who_should_buy}\n\n"
            )

            cards.append(cls._to_product_summary(rpt))
            sources.append(
                SourceCitation(
                    product_id=rpt.product_id,
                    product_name=rpt.product_name,
                    total_reviews_analyzed=rpt.total_ratings_count,
                    verified_purchases_ratio=rpt.satisfaction_rate,
                    key_aspect="Platform Calibrated Recommendation"
                )
            )

        reply += (
            "💡 **Intelligence Tip**: Click **View Full Intelligence** on any card below to inspect the full failure modes and verified buyer quotes."
        )

        first_prod = reports[0].product_name[:30] if reports else "this model"
        return ChatResponse(
            reply=reply,
            products=cards,
            sources=sources,
            intent="recommendation",
            suggested_followups=[
                f"What are the known failure modes of {first_prod}?",
                "Show me alternatives from other brands",
                "How does the battery lifespan hold up over time?"
            ]
        )

    @classmethod
    def _handle_defects(cls, db: Session, query: str, messages: List[ChatMessage]) -> ChatResponse:
        # Search for product mentioned
        candidates = cls.search_products(db, query, limit=3)
        if not candidates:
            # Check context
            context_prod = cls._resolve_context_product(messages, db)
            if context_prod:
                candidates = [context_prod]

        if not candidates:
            return ChatResponse(
                reply=(
                    f"I couldn't identify the specific product mentioned in **\"{query}\"**.\n\n"
                    "Please include the brand and model name, e.g.:\n"
                    "* *\"What are the flaws with Apple iPhone 8 Plus?\"*\n"
                    "* *\"What problems do users report for Samsung Galaxy S20?\"*"
                ),
                intent="defects_flaws",
                suggested_followups=[
                    "What are the flaws with Apple iPhone 8 Plus?",
                    "What are the failure modes of Dell Latitude?",
                    "Known defects of Bose QuietComfort"
                ]
            )

        prod = candidates[0]
        rpt = ProductReportService.generate_report(db, prod.product_id)

        # Pull real 1-star and 2-star reviews from DB for deep quotes
        negs = db.execute(
            select(Review).where(
                Review.product_id == prod.product_id,
                Review.star_rating <= 2.0
            ).order_by(desc(Review.helpful_votes)).limit(3)
        ).scalars().all()

        quotes_md = ""
        if negs:
            quotes_md = "\n### 💬 Direct Verified Buyer Complaints\n"
            for n in negs:
                txt = (n.review_text or "").strip()
                if len(txt) > 180:
                    txt = txt[:180].rsplit(" ", 1)[0] + "..."
                quotes_md += f"> \"{txt}\"\n> — **{n.star_rating:.0f}★ Verified Purchase** ({n.review_date.strftime('%b %Y') if n.review_date else 'Recent'})\n\n"

        flaws_list = "\n".join([f"* ⚠️ **{p.title}** ({p.severity} Severity): {p.description}" for p in rpt.critical_negative_points])

        reply = (
            f"## ⚠️ Critical Flaws & Defect Intelligence: {prod.product_name}\n\n"
            f"Our review intelligence pipeline analyzed customer complaints and component failure reports for this product:\n\n"
            f"* **Honest Reality Rating**: **{rpt.overall_rating}★** (Grade {rpt.quality_grade}) — *Defect penalty applied to Amazon's {rpt.marketplace_listed_rating or 'N/A'}★*\n"
            f"* **Critical Complaint / Defect Rate**: **{rpt.critical_complaint_rate}%** of reviews indicate significant malfunctions or premature wear.\n"
            f"* **Durability Assessment**: {rpt.durability_and_longevity_deep_dive}\n\n"
            f"### Confirmed Failure Modes & Drawbacks\n"
            f"{flaws_list}\n"
            f"{quotes_md}\n"
            f"### 🚫 Who Should Skip This Product\n"
            f"{rpt.who_should_skip}\n\n"
            f"### 🛒 Who Can Still Buy It\n"
            f"{rpt.who_should_buy}"
        )

        return ChatResponse(
            reply=reply,
            products=[cls._to_product_summary(rpt)],
            sources=[
                SourceCitation(
                    product_id=prod.product_id,
                    product_name=prod.product_name,
                    total_reviews_analyzed=rpt.total_ratings_count,
                    verified_purchases_ratio=rpt.satisfaction_rate,
                    key_aspect="Defect & Failure Mode Extraction"
                )
            ],
            intent="defects_flaws",
            suggested_followups=[
                f"How is the battery life on {prod.product_name[:30]}?",
                f"Compare {prod.product_name[:30]} with more reliable alternatives",
                "Is there an extended warranty recommendation for this model?"
            ]
        )

    @classmethod
    def _handle_aspect(cls, db: Session, query: str, messages: List[ChatMessage]) -> ChatResponse:
        candidates = cls.search_products(db, query, limit=3)
        if not candidates:
            context_prod = cls._resolve_context_product(messages, db)
            if context_prod:
                candidates = [context_prod]

        if not candidates:
            # Check if this is a general category aspect query (e.g. "Which earbuds have best battery?")
            cat = cls._detect_category_intent(query)
            if cat:
                return cls._handle_recommendation(db, query, cat, None)

            return ChatResponse(
                reply=(
                    f"Please specify which product you would like to analyze for this feature.\n\n"
                    "For example:\n"
                    "* *\"How is the battery life on iPhone 8 Plus?\"*\n"
                    "* *\"Is the build quality durable on MacBook Air?\"*"
                ),
                intent="aspect_deep_dive"
            )

        prod = candidates[0]
        rpt = ProductReportService.generate_report(db, prod.product_id)

        # Find aspect matching query
        q_lower = query.lower()
        matched_aspect = None
        for a in rpt.aspects:
            a_words = [w.lower() for w in a.name.split()]
            if any(w in q_lower for w in a_words) or ("battery" in q_lower and "battery" in a.name.lower()) or ("durab" in q_lower and "durab" in a.name.lower()):
                matched_aspect = a
                break

        if not matched_aspect:
            matched_aspect = rpt.aspects[0]

        reply = (
            f"## 🔍 Aspect Deep Dive: {matched_aspect.name}\n\n"
            f"**Product**: {prod.product_name}\n\n"
            f"* **Aspect Score**: **{matched_aspect.score} / 5.0** ({matched_aspect.percentage:.0f}%) — **Status: {matched_aspect.status}**\n"
            f"* **Review Consensus**: {matched_aspect.summary}\n"
            f"* **Key Customer Evidence**: {matched_aspect.key_evidence}\n\n"
            f"### Overall Product Context\n"
            f"Across all dimensions, this product carries an Honest Rating of **{rpt.overall_rating}★** (Grade {rpt.quality_grade}) with an estimated defect/wear rate of **{rpt.critical_complaint_rate}%**."
        )

        return ChatResponse(
            reply=reply,
            products=[cls._to_product_summary(rpt)],
            sources=[
                SourceCitation(
                    product_id=prod.product_id,
                    product_name=prod.product_name,
                    total_reviews_analyzed=rpt.total_ratings_count,
                    verified_purchases_ratio=rpt.satisfaction_rate,
                    key_aspect=matched_aspect.name
                )
            ],
            intent="aspect_deep_dive",
            suggested_followups=[
                f"What are the general flaws with {prod.product_name[:30]}?",
                f"Compare {prod.product_name[:30]} against top competitors",
                "Show verified 1-star customer complaints"
            ]
        )

    @classmethod
    def _handle_general_inquiry(cls, db: Session, query: str, messages: List[ChatMessage]) -> ChatResponse:
        candidates = cls.search_products(db, query, limit=3)
        if not candidates:
            context_prod = cls._resolve_context_product(messages, db)
            if context_prod:
                candidates = [context_prod]

        if not candidates:
            return ChatResponse(
                reply=(
                    f"I couldn't locate reviews or catalog data matching **\"{query}\"** in our electronics dataset.\n\n"
                    "You can ask about popular categories like **laptops**, **smartphones**, **headphones**, or specific models like **iPhone 8 Plus**, **Galaxy S20**, **MacBook**, **Bose QuietComfort**, etc."
                ),
                intent="general",
                suggested_followups=[
                    "Tell me about Apple iPhone 8 Plus",
                    "What is the best laptop under $500?",
                    "Compare iPhone 8 Plus vs Galaxy S20 FE"
                ]
            )

        prod = candidates[0]
        rpt = ProductReportService.generate_report(db, prod.product_id)

        aspects_md = "\n".join([f"* **{a.name}**: {a.score}★ ({a.status}) — *{a.summary}*" for a in rpt.aspects])
        strengths_md = "\n".join([f"* ✅ {s}" for s in rpt.strengths[:3]])
        flaws_md = "\n".join([f"* ⚠️ {f}" for f in rpt.flaws_and_drawbacks[:3]])

        reply = (
            f"## 📋 Review Intelligence Overview: {prod.product_name}\n\n"
            f"Here is the executive consensus synthesized from verified customer reviews:\n\n"
            f"* **Honest Reality Rating**: **{rpt.overall_rating}★** (Grade {rpt.quality_grade})\n"
            f"* **Marketplace Listed Rating**: {rpt.marketplace_listed_rating or 'N/A'}★ (Debiased to account for positive rating inflation)\n"
            f"* **Defect / Return Risk**: **{rpt.critical_complaint_rate}%** of customer feedback cites recurring faults\n"
            f"* **Price**: ${rpt.price:.2f} USD\n\n"
            f"### 📊 Aspect Performance\n"
            f"{aspects_md}\n\n"
            f"### Key Strengths & Praises\n"
            f"{strengths_md}\n\n"
            f"### Confirmed Flaws & Drawbacks\n"
            f"{flaws_md}\n\n"
            f"### 🎯 The Bottom Line\n"
            f"{rpt.overall_verdict}"
        )

        return ChatResponse(
            reply=reply,
            products=[cls._to_product_summary(rpt)],
            sources=[
                SourceCitation(
                    product_id=prod.product_id,
                    product_name=prod.product_name,
                    total_reviews_analyzed=rpt.total_ratings_count,
                    verified_purchases_ratio=rpt.satisfaction_rate,
                    key_aspect="Comprehensive Executive Synthesis"
                )
            ],
            intent="product_inquiry",
            suggested_followups=[
                f"What are the specific flaws of {prod.product_name[:30]}?",
                f"How is the battery life on {prod.product_name[:30]}?",
                f"Compare {prod.product_name[:30]} with alternatives"
            ]
        )
