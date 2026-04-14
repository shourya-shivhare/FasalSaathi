# app/services/scheme_service.py

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.models.scheme import Scheme
from app.models.user import User
from app.schemas.scheme import SchemeRecommendation


class SchemeService:
    def __init__(self, db: Session):
        self.db = db

    # 🔥 Recommendation (returns SchemeRecommendation)
    def recommend(self, user: User) -> List[SchemeRecommendation]:
        q = self.db.query(Scheme)

        # State filter
        if user.state:
            q = q.filter(
                or_(
                    Scheme.states.contains(["ALL"]),
                    Scheme.states.contains([user.state])
                )
            )

        # Crop filter
        if user.crops_grown:
            q = q.filter(
                or_(
                    Scheme.crops.is_(None),
                    Scheme.crops.overlap(user.crops_grown)
                )
            )

        # Age filter
        if user.age is not None:
            q = q.filter(
                or_(Scheme.min_age.is_(None), Scheme.min_age <= user.age)
            )
            q = q.filter(
                or_(Scheme.max_age.is_(None), Scheme.max_age >= user.age)
            )

        schemes = q.all()

        results = []
        for scheme in schemes:
            score, matched = self._score(scheme, user)

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
    def list(self, category: str | None, state: str | None) -> List[Scheme]:
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

        return q.all()

    # 🔹 Scoring logic
    def _score(self, scheme: Scheme, user: User):
        score = 0
        matched = []

        # State
        if scheme.states:
            if "ALL" in scheme.states:
                score += 0.2
                matched.append("state:ALL")
            elif user.state and user.state in scheme.states:
                score += 0.4
                matched.append(f"state:{user.state}")

        # Crop
        if scheme.crops and user.crops_grown:
            for crop in user.crops_grown:
                if crop in scheme.crops:
                    score += 0.3
                    matched.append(f"crop:{crop}")
                    break

        # Age
        if user.age is not None:
            if scheme.min_age and user.age >= scheme.min_age:
                score += 0.1
                matched.append("age:min")
            if scheme.max_age and user.age <= scheme.max_age:
                score += 0.1
                matched.append("age:max")

        return min(score, 1.0), matched