import pytest
from ai_service.app.core.crop_knowledge_base import CropKnowledgeBaseService


def test_knowledge_base_loading():
    """Assert that the service loads all 9 seed crops from JSON."""
    service = CropKnowledgeBaseService()
    crops = service.list_all_crops()
    assert len(crops) == 9
    
    crop_names = {c.crop_name.lower() for c in crops}
    expected = {"rice", "maize", "soybean", "wheat", "mustard", "gram (chana)", "moong", "watermelon", "cucumber"}
    assert expected.issubset(crop_names)


def test_get_crop_profile_case_insensitive():
    """Assert crop profile retrieval by name is case-insensitive."""
    service = CropKnowledgeBaseService()
    rice = service.get_crop_profile("Rice")
    assert rice is not None
    assert rice.crop_name == "Rice"
    assert rice.scientific_name == "Oryza sativa"
    assert rice.season == "Kharif"
    assert rice.ideal_ph.min == 5.5
    assert rice.ideal_ph.max == 6.5
    assert rice.nitrogen_requirement_kg_ha == 120.0

    wheat = service.get_crop_profile("WHEAT")
    assert wheat is not None
    assert wheat.crop_name == "Wheat"
    assert wheat.season == "Rabi"

    gram = service.get_crop_profile("gram (chana)")
    assert gram is not None
    assert gram.crop_name == "Gram (Chana)"

    non_existent = service.get_crop_profile("NonExistentCrop")
    assert non_existent is None


def test_find_crops_by_filters():
    """Assert geographical and soil suitability filtering logic."""
    service = CropKnowledgeBaseService()
    
    # 1. State filter
    mp_crops = service.find_crops_by_filters(state="Madhya Pradesh")
    assert len(mp_crops) > 0
    mp_names = {c.crop_name.lower() for c in mp_crops}
    assert "soybean" in mp_names
    assert "wheat" in mp_names

    # 2. Season filter
    rabi_crops = service.find_crops_by_filters(state="Madhya Pradesh", season="Rabi")
    assert len(rabi_crops) > 0
    for c in rabi_crops:
        assert c.season == "Rabi"

    # 3. Soil type filter
    sandy_crops = service.find_crops_by_filters(state="Rajasthan", soil_type="Sandy")
    assert len(sandy_crops) > 0
    sandy_names = {c.crop_name.lower() for c in sandy_crops}
    assert "mustard" in sandy_names
    assert "moong" in sandy_names
    assert "rice" not in sandy_names  # Rice does not grow in sandy soil in our profiles
