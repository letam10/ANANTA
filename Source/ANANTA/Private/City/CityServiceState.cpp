#include "City/CityServiceState.h"

bool FCityServiceState::IsServiceId(const FName Id, const ECityServiceKind Kind)
{
    if (Id.IsNone())
    {
        return false;
    }
    switch (Kind)
    {
    case ECityServiceKind::Rest:
        return Id == TEXT("Cafe_Rest") || Id == TEXT("Apartment_Rest");
    case ECityServiceKind::Heal:
        return Id == TEXT("Clinic_Heal");
    case ECityServiceKind::Supplies:
    {
        const FString Name = Id.ToString();
        return Id == TEXT("Market_Supplies")
            || (Name.StartsWith(TEXT("Supply_")) && Name.Len() > 7);
    }
    case ECityServiceKind::Read:
        return Id == TEXT("Bookshop_Read") || Id == TEXT("Gallery_Read")
            || Id == TEXT("Workshop_Read") || Id == TEXT("Transit_Read")
            || Id == TEXT("Police_Read") || Id == TEXT("Fire_Read")
            || Id == TEXT("Bar_Read") || Id == TEXT("Arcade_Read");
    default:
        return false;
    }
}

bool FCityServiceState::Discover(const FName Id)
{
    if (!IsValid() || !IsVisitId(Id) || VisitedIds.Contains(Id))
    {
        return false;
    }
    VisitedIds.Add(Id);
    return true;
}

bool FCityServiceState::IsVisitId(const FName Id)
{
    return IsServiceId(Id, ECityServiceKind::Rest) || IsServiceId(Id, ECityServiceKind::Heal)
        || IsServiceId(Id, ECityServiceKind::Supplies) || IsServiceId(Id, ECityServiceKind::Read);
}

bool FCityServiceState::ClaimSupply(const FName Id)
{
    if (!IsValid() || !IsServiceId(Id, ECityServiceKind::Supplies) || ClaimedSupplyIds.Contains(Id)
        || SuppliesCount == MAX_int32)
    {
        return false;
    }
    ClaimedSupplyIds.Add(Id);
    ++SuppliesCount;
    return true;
}

bool FCityServiceState::IsValid() const
{
    // Chua co tieu hao vat tu: moi ID da nhan phai ung voi dung mot don vi.
    if (SuppliesCount < 0 || SuppliesCount != ClaimedSupplyIds.Num())
    {
        return false;
    }
    for (const FName Id : VisitedIds)
    {
        if (!IsVisitId(Id))
        {
            return false;
        }
    }
    for (const FName Id : ClaimedSupplyIds)
    {
        if (!IsServiceId(Id, ECityServiceKind::Supplies))
        {
            return false;
        }
    }
    return true;
}
