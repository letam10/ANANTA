#if WITH_DEV_AUTOMATION_TESTS
#include "City/Mobility/CityMobilityData.h"
#include "City/CityWorldBounds.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityTransportRoutesTest, "ANANTA.City.Mobility.AuthoredRoutes",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityTransportRoutesTest::RunTest(const FString& Parameters)
{
    TSet<FName> Names;
    for (int32 Index = 0; Index < static_cast<int32>(ECityTransportKind::Count); ++Index)
    {
        const auto Kind = static_cast<ECityTransportKind>(Index);
        const auto Route = CityMobility::MakeRoute(Kind);
        TestFalse(TEXT("Unique fleet identity"), Names.Contains(Route.Id));
        Names.Add(Route.Id);
        TestTrue(TEXT("Closed route has corners"), Route.Points.Num() >= 4);
        TestTrue(TEXT("Route has an authored stop"), !Route.Stops.IsEmpty());
        for (const int32 Stop : Route.Stops)
        {
            TestTrue(TEXT("Valid stop index"), Route.Points.IsValidIndex(Stop));
        }
        for (int32 Point = 0; Point < Route.Points.Num(); ++Point)
        {
            const FVector Current = Route.Points[Point];
            const FVector Next = Route.Points[(Point + 1) % Route.Points.Num()];
            TestTrue(TEXT("Point inside city"), FMath::Abs(Current.X) < CityWorldBounds::RoadExtent
                && FMath::Abs(Current.Y) < CityWorldBounds::RoadExtent);
            TestTrue(TEXT("Nonzero route segment"), FVector::Dist2D(Current, Next) > 1000);
            TestTrue(TEXT("Fixed main-road axes"), FMath::IsNearlyEqual(Current.X, Next.X)
                || FMath::IsNearlyEqual(Current.Y, Next.Y));
            if (Route.bWater)
            {
                TestTrue(TEXT("Vessels stay in coastal water corridor"), Current.X > 120000
                    && Current.Y < -120000 && Current.Z == CityMobility::WaterLevel);
            }
            else
            {
                const float LaneX = FMath::Abs(FMath::GridSnap(Current.X, 12000.f) - Current.X);
                const float LaneY = FMath::Abs(FMath::GridSnap(Current.Y, 12000.f) - Current.Y);
                TestTrue(TEXT("Road point lies on lane"), FMath::IsNearlyEqual(LaneX, 420.f)
                    || FMath::IsNearlyEqual(LaneY, 420.f));
            }
        }
    }
    TestEqual(TEXT("All requested transport types"), Names.Num(), 11);
    return true;
}
#endif
