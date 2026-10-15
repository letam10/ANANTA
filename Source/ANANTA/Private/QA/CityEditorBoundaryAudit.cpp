#include "QA/CityEditorTools.h"

#include "Components/PrimitiveComponent.h"
#include "Engine/World.h"

FString UCityEditorTools::AuditWorldBoundaries(UWorld* World, double ExtentCm)
{
#if WITH_EDITOR
    if (!World || !FMath::IsFinite(ExtentCm) || ExtentCm <= 0)
    {
        return TEXT("passed=0\nerror=Missing world or invalid extent\n");
    }
    int32 Samples = 0;
    int32 Errors = 0;
    FString Detail;
    const auto Check = [&](const FVector& Start, const FVector& End)
    {
        ++Samples;
        FHitResult Hit;
        const FCollisionQueryParams Params(SCENE_QUERY_STAT(CityWorldBoundary), false);
        const bool bHit = World->SweepSingleByChannel(Hit, Start, End, FQuat::Identity,
            ECC_Pawn, FCollisionShape::MakeCapsule(38, 92), Params);
        const UPrimitiveComponent* Component = Hit.GetComponent();
        const bool bHidden = Component && !Component->IsVisible();
        const double ImpactEdge = FMath::Max(FMath::Abs(Hit.ImpactPoint.X), FMath::Abs(Hit.ImpactPoint.Y));
        const double CentreEdge = FMath::Max(FMath::Abs(Hit.Location.X), FMath::Abs(Hit.Location.Y));
        const bool bEdge = FMath::Abs(ImpactEdge - ExtentCm) <= 2 && CentreEdge < ExtentCm - 37;
        if (!bHit || !Hit.bBlockingHit || Hit.bStartPenetrating || !bHidden || !bEdge)
        {
            ++Errors;
            Detail += FString::Printf(TEXT("boundaryInvalid=%s hit=%s hidden=%d edge=%.2f centre=%.2f\n"),
                *Start.ToString(), *GetNameSafe(Hit.GetActor()), bHidden, ImpactEdge, CentreEdge);
        }
    };
    // Capsule giu nguyen kich thuoc nhan vat; khong dung clamp toa do de thay cho collider.
    for (const double Sign : {-1.0, 1.0})
    {
        for (const double Height : {112.0, 2012.0})
        {
            Check(FVector(Sign * (ExtentCm - 200), 0, Height), FVector(Sign * (ExtentCm + 200), 0, Height));
            Check(FVector(0, Sign * (ExtentCm - 200), Height), FVector(0, Sign * (ExtentCm + 200), Height));
        }
    }
    Check(FVector(ExtentCm - 200, -130000, -20), FVector(ExtentCm + 200, -130000, -20));
    Check(FVector(130000, -ExtentCm + 200, -20), FVector(130000, -ExtentCm - 200, -20));
    for (const double XSign : {-1.0, 1.0})
    {
        for (const double YSign : {-1.0, 1.0})
        {
            Check(FVector(XSign * (ExtentCm - 200), YSign * (ExtentCm - 200), 112),
                FVector(XSign * (ExtentCm + 200), YSign * (ExtentCm + 200), 112));
        }
    }
    return FString::Printf(TEXT("passed=%d\nboundarySamples=%d\nerrors=%d\n"),
        Errors == 0 && Samples == 14, Samples, Errors) + Detail;
#else
    return TEXT("passed=0\nerror=Editor only\n");
#endif
}
