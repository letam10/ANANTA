#if WITH_DEV_AUTOMATION_TESTS
#include "City/Mobility/CityMobilityData.h"
#include "City/CityWorldBounds.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityRegionalRoutesTest, "ANANTA.City.Mobility.RegionalRoadCoverage",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityRegionalRoutesTest::RunTest(const FString& Parameters)
{
    const auto ClosestStop = [](const FCityTransportRoute& Route, const FVector& Player)
    {
        double Distance = TNumericLimits<double>::Max();
        for (const int32 Stop : Route.Stops)
        {
            Distance = FMath::Min(Distance, FVector::Dist2D(Player, Route.Points[Stop]));
        }
        return Distance;
    };
    const FVector East(200000, 0, 100);
    TestTrue(TEXT("Legacy core routes miss the expanded east district"),
        ClosestStop(CityMobility::MakeRoute(ECityTransportKind::Coach), East) > CityMobility::ActivationDistance);
    const FVector Samples[] = {
        East, FVector(-244000, 420, 100), FVector(-244000, -215580, 100),
        FVector(-244000, 216420, 100), FVector(-28000, -215580, 100),
        FVector(-28000, 216420, 100), FVector(188000, 288420, 100)
    };
    for (const FVector& Player : Samples)
    {
        const auto Route = CityMobility::MakeNearbyRoute(ECityTransportKind::Coach, Player);
        const double Distance = ClosestStop(Route, Player);
        TestTrue(TEXT("Authored regional stop activates from this distant main road"),
            Distance >= 1800 && Distance <= CityMobility::ActivationDistance);
        for (const FVector& Point : Route.Points)
        {
            TestTrue(TEXT("Regional coach stays inside playable roads"),
                FMath::Abs(Point.X) < CityWorldBounds::RoadExtent
                && FMath::Abs(Point.Y) < CityWorldBounds::RoadExtent
                && !CityWorldBounds::IsStreetCutout(Point.X, Point.Y));
        }
    }
    for (int32 Index = 0; Index < static_cast<int32>(ECityTransportKind::Count); ++Index)
    {
        const auto Kind = static_cast<ECityTransportKind>(Index);
        const auto Base = CityMobility::MakeRoute(Kind);
        const auto Nearby = CityMobility::MakeNearbyRoute(Kind, East);
        if (Base.bWater || Base.bRail)
        {
            TestTrue(TEXT("Authored harbor and rail routes retain their exact points"), Base.Points == Nearby.Points);
            TestEqual(TEXT("Authored harbor and rail identity unchanged"), Nearby.Id, Base.Id);
        }
        else
        {
            for (int32 Point = 0; Point < Nearby.Points.Num(); ++Point)
            {
                const FVector Current = Nearby.Points[Point];
                const FVector Next = Nearby.Points[(Point + 1) % Nearby.Points.Num()];
                const FVector Middle = (Current + Next) * .5;
                TestTrue(TEXT("Regional roads avoid water and airport cutouts"),
                    !CityWorldBounds::IsStreetCutout(Current.X, Current.Y)
                    && !CityWorldBounds::IsStreetCutout(Middle.X, Middle.Y));
                TestTrue(TEXT("Regional route retains fixed road axes"),
                    FMath::IsNearlyEqual(Current.X, Next.X) || FMath::IsNearlyEqual(Current.Y, Next.Y));
            }
        }
    }
    return true;
}
#endif
