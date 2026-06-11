# app/services/scheme_service.py

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from backend.app.models.scheme import Scheme
from backend.app.models.user import User
from backend.app.schemas.scheme import SchemeRecommendation


class SchemeService:
    def __init__(self, db: Session):
        self.db = db

    # 🔥 Recommendation (returns SchemeRecommendation)
    def recommend(self, user: User) -> List[SchemeRecommendation]:
        from backend.app.services.context_builder import build_farmer_context
        context = build_farmer_context(user.id, self.db)
        
        q = self.db.query(Scheme)

        # State filter
        state = context.get("state")
        if state:
            q = q.filter(
                or_(
                    Scheme.states.contains(["ALL"]),
                    Scheme.states.contains([state])
                )
            )

        # Crop filter
        active_crops = context.get("active_crops")
        if active_crops:
            q = q.filter(
                or_(
                    Scheme.crops.is_(None),
                    Scheme.crops.overlap(active_crops)
                )
            )

        # Age filter
        age = user.farmer_profile.age if (user.farmer_profile and user.farmer_profile.age) else user.age
        if age is not None:
            q = q.filter(
                or_(Scheme.min_age.is_(None), Scheme.min_age <= age)
            )
            q = q.filter(
                or_(Scheme.max_age.is_(None), Scheme.max_age >= age)
            )

        schemes = q.all()

        results = []
        for scheme in schemes:
            score, matched = self._score(scheme, user, context)

            results.append(
                SchemeRecommendation(
                    id=scheme.id,
                    name=scheme.name,
                    ministry=scheme.ministry,
                    category=scheme.category,
                    description=scheme.description,
                    benefits=scheme.benefits,
                    eligibility=scheme.eligibility,
                    states=scheme.states,
                    crops=scheme.crops,
                    min_age=scheme.min_age,
                    max_age=scheme.max_age,
                    apply_url=scheme.apply_url,
                    source=scheme.source,
                    last_synced=scheme.last_synced,
                    match_score=score,
                    matched_on=matched
                )
            )

        return sorted(results, key=lambda x: x.match_score, reverse=True)

    # 🔹 Simple list API
    def list(self, category: str | None, state: str | None, crop: str | None = None, skip: int = 0, limit: int = 50) -> List[Scheme]:
        q = self.db.query(Scheme)

        if category:
            q = q.filter(Scheme.category == category)

        if state:
            q = q.filter(
                or_(
                    Scheme.states.contains(["ALL"]),
                    Scheme.states.contains([state])
                )
            )

        if crop:
            q = q.filter(
                or_(
                    Scheme.crops.is_(None),
                    Scheme.crops.contains([crop])
                )
            )

        return q.offset(skip).limit(limit).all()

    # 🔹 Scoring logic
    def _score(self, scheme: Scheme, user: User, context: dict):
        score = 0
        matched = []

        # State
        state = context.get("state")
        if scheme.states:
            if "ALL" in scheme.states:
                score += 0.2
                matched.append("state:ALL")
            elif state and state in scheme.states:
                score += 0.4
                matched.append(f"state:{state}")

        # Crop
        active_crops = context.get("active_crops")
        if scheme.crops and active_crops:
            for crop in active_crops:
                if crop in scheme.crops:
                    score += 0.3
                    matched.append(f"crop:{crop}")
                    break

        # Age
        age = user.farmer_profile.age if (user.farmer_profile and user.farmer_profile.age) else user.age
        if age is not None:
            if scheme.min_age and age >= scheme.min_age:
                score += 0.1
                matched.append("age:min")
            if scheme.max_age and age <= scheme.max_age:
                score += 0.1
                matched.append("age:max")

        return min(score, 1.0), matched