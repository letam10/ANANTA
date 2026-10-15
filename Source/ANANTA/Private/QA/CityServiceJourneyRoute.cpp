#include "QA/CityServiceJourney.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"

namespace
{
    struct FServiceDoor
    {
        double FrontX;
        double CentreY;
        double SidewalkX;
        FVector Service;
    };

    // Toa do theo CityExpansionData.py va CityExpansionVenues.py; giu nguyen cua cac phong cu.
    const FServiceDoor Doors[] = {
        { -25350, 2400, -25100, FVector(-26000, 2400, 100) },
        { -22600, -2800, -22900, FVector(-22270, -2800, 80) },
        { -37350, 2700, -37100, FVector(-37680, 2700, 80) },
        { -10550, 2550, -10900, FVector(-10220, 2550, 80) },
        { 1350, 2500, 1100, FVector(2200, 2600, 95) },
        { 13350, 2550, 13100, FVector(13680, 2550, 80) },
        { 37350, 2500, 37100, FVector(37680, 2500, 80) },
        { 61350, 2500, 61100, FVector(61680, 2500, 80) }
    };
}

FName UCityServiceJourney::ServiceId(const int32 Index) const
{
    static const FName Ids[] = {
        TEXT("Cafe_Rest"), TEXT("Market_Supplies"), TEXT("Bookshop_Read"), TEXT("Clinic_Heal"),
        TEXT("Apartment_Rest"), TEXT("Gallery_Read"), TEXT("Workshop_Read"), TEXT("Transit_Read")
    };
    return Index >= 0 && Index < UE_ARRAY_COUNT(Ids) ? Ids[Index] : NAME_None;
}

void UCityServiceJourney::AddEntry(const int32 Index, const bool bReverse)
{
    const auto& Door = Doors[Index];
    const double Face = Door.SidewalkX > Door.FrontX ? 1 : -1;
    const FVector Approach(Door.Service.X + Face * 160, Door.Service.Y, 100);
    const TArray<FVector> Entry = {
        FVector(Door.SidewalkX, Door.CentreY, 100),
        FVector(Door.FrontX + Face * 130, Door.CentreY, 100),
        FVector(Door.FrontX - Face * 150, Door.CentreY, 100),
        FVector(Approach.X, Door.CentreY, 100), Approach
    };
    // Dao thu tu cua lo vao de ra phong; khong cat duong cheo xuyen vo nha.
    for (int32 Step = 0; Step < Entry.Num(); ++Step)
    {
        Waypoints.Add(Entry[bReverse ? Entry.Num() - Step - 1 : Step]);
    }
}

void UCityServiceJourney::BeginRoute()
{
    Waypoints.Empty();
    Waypoint = 0;
    if (Venue > 0)
    {
        AddEntry(Venue - 1, true);
        const auto& Previous = Doors[Venue - 1];
        const double PreviousLane = Previous.CentreY < 0 ? -1100 : 1100;
        Waypoints.Add(FVector(Previous.SidewalkX, PreviousLane, 100));
    }
    else
    {
        Waypoints.Add(FVector(Doors[0].SidewalkX, GetHero()->GetActorLocation().Y, 100));
    }
    const auto& Door = Doors[Venue];
    const double Lane = Door.CentreY < 0 ? -1100 : 1100;
    if (Venue > 0)
    {
        const double PreviousLane = Doors[Venue - 1].CentreY < 0 ? -1100 : 1100;
        Waypoints.Add(FVector(Door.SidewalkX, PreviousLane, 100));
        Waypoints.Add(FVector(Door.SidewalkX, Lane, 100));
    }
    AddEntry(Venue, false);
    NextPhase(ECityServiceJourneyPhase::Route,
        FString::Printf(TEXT("Walk through doorway to %s"), *ServiceId(Venue).ToString()));
}

void UCityServiceJourney::BeginExit()
{
    bLeavingLastVenue = true;
    Waypoints.Empty();
    Waypoint = 0;
    AddEntry(Venue, true);
    Waypoints.Add(FVector(Doors[Venue].SidewalkX, 1100, 100));
    NextPhase(ECityServiceJourneyPhase::Route, TEXT("Reverse final doorway route to sidewalk save location"));
}

bool UCityServiceJourney::WalkToward(const FVector& Destination)
{
    FVector Direction = Destination - GetHero()->GetActorLocation();
    Direction.Z = 0;
    const double Distance = Direction.Size();
    const bool bReached = Distance <= 24;
    SetKey(EKeys::W, !bReached);
    SetKey(EKeys::LeftShift, !bReached && Distance > 500);
    if (!bReached)
    {
        Controller->SetControlRotation(FRotator(-12, Direction.Rotation().Yaw, 0));
        if (FVector::Dist2D(MotionOrigin, GetHero()->GetActorLocation()) > 80)
        {
            MotionOrigin = GetHero()->GetActorLocation();
            MotionTime = Now;
        }
        else if (Now - MotionTime > 12)
        {
            Finish(false, TEXT("Ordinary movement blocked for 12 seconds"));
        }
    }
    else
    {
        MotionOrigin = GetHero()->GetActorLocation();
        MotionTime = Now;
    }
    return bReached;
}
