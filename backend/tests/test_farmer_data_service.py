from backend.app.models.crop_cycle import CropCycle
from backend.app.models.farm import Farm
from backend.app.models.pest_detection_history import PestDetectionHistory
from backend.app.models.user import User
from backend.app.models.enums import CropCycleStatus, CropSeason
from backend.app.services.context_builder import ContextBuilder, build_farmer_context
from backend.app.services.farmer_data_service import FarmerDataService


def _user(suffix: str) -> User:
    return User(
        username=f"data-test-{suffix}",
        phone_number=f"90000000{suffix}",
        password_hash="not-used",
    )


def test_service_and_context_exclude_other_users_records(db):
    owner = _user("01")
    other = _user("02")
    db.add_all([owner, other])
    db.flush()

    owner_farm = Farm(
        user_id=owner.id,
        farm_name="Owner Farm",
        total_area=3.5,
        latitude=22.7196,
        longitude=75.8577,
        ph=6.5,
    )
    other_farm = Farm(user_id=other.id, farm_name="Private Farm", total_area=99)
    db.add_all([owner_farm, other_farm])
    db.flush()

    owner_crop = CropCycle(
        farm_id=owner_farm.id,
        crop_name="Wheat",
        season=CropSeason.RABI,
        status=CropCycleStatus.ACTIVE,
    )
    other_crop = CropCycle(
        farm_id=other_farm.id,
        crop_name="Secret Crop",
        season=CropSeason.KHARIF,
        status=CropCycleStatus.ACTIVE,
    )
    db.add_all([owner_crop, other_crop])
    db.flush()
    db.add_all([
        PestDetectionHistory(user_id=owner.id, disease_name="Rust"),
        PestDetectionHistory(user_id=other.id, disease_name="Private Disease"),
    ])
    db.flush()

    service_context = FarmerDataService(db, owner.id).get_full_context()
    rich_context = ContextBuilder(db).build(owner)
    legacy_context = build_farmer_context(owner.id, db)

    assert [farm["farm_name"] for farm in service_context["farms"]] == ["Owner Farm"]
    assert [crop["crop_name"] for crop in service_context["active_crops"]] == ["Wheat"]
    assert [pest["disease_name"] for pest in service_context["pest_history"]] == ["Rust"]
    
    # Assertions on the new Pydantic FarmerContext object
    assert rich_context.farm_summary.total_registered_area == 3.5
    assert len(rich_context.farms) == 1
    assert rich_context.farms[0].farm_name == "Owner Farm"
    assert rich_context.farms[0].gps_coordinates.latitude == 22.7196
    assert rich_context.farms[0].gps_coordinates.longitude == 75.8577
    assert rich_context.soil_profiles[0].ph == 6.5
    
    # Check that weather data was fetched (since latitude/longitude are set)
    assert rich_context.weather_data is not None
    assert rich_context.weather_data.lat == 22.7196
    assert rich_context.weather_data.current.temperature_c is not None

    # Assertion on legacy shape
    assert legacy_context["active_crops"] == ["Wheat"]
    
    # Verify separation
    rich_context_str = str(rich_context.model_dump())
    assert "Private Farm" not in rich_context_str
    assert "Secret Crop" not in rich_context_str
    assert "Private Disease" not in rich_context_str


def test_empty_context_has_stable_shapes(db):
    user = _user("03")
    db.add(user)
    db.flush()

    context = ContextBuilder(db).build(user)

    assert context.farms == []
    assert context.active_crops == []
    assert context.pest_history == []
    assert context.farm_summary.total_farms == 0
    assert context.weather_data is None
