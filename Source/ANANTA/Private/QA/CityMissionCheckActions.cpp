#include "QA/CityMissionCheckSubsystem.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACityEnemy.h"
#include "City/ANANTACityInteractable.h"
#include "City/ANANTACitySubsystem.h"
#include "Engine/World.h"
#include "EngineUtils.h"

FName UCityMissionCheckSubsystem::ObjectiveId() const
{
    static const FName Ids[] = {
        TEXT("Giver_Cafe"), TEXT("Clue_01"), TEXT("Clue_02"), TEXT("Clue_03"),
        TEXT("Fragment_Anomaly"), TEXT("Giver_Cafe")
    };
    return Ids[Objective];
}

AANANTACityInteractable* UCityMissionCheckSubsystem::FindItem(const FName Id) const
{
    AANANTACityInteractable* Result = nullptr;
    for (TActorIterator<AANANTACityInteractable> It(GetWorld()); It; ++It)
    {
        if (It->InteractionId == Id)
        {
            if (Result)
            {
                return nullptr;
            }
            Result = *It;
        }
    }
    return Result;
}

void UCityMissionCheckSubsystem::BeginRoute()
{
    static const FVector Anchors[] = {
        FVector(-25000, 2400, 110), FVector(-12000, 1800, 100), FVector(1000, 1800, 100),
        FVector(24500, 2400, 100), FVector(26000, 4500, 100), FVector(-25000, 2400, 110)
    };
    Waypoints.Empty();
    Waypoint = 0;
    const FVector Destination = Anchors[Objective] - FVector(0, 220, 0);
    if (Objective != 0 && Objective != 4)
    {
        // Di theo via he truc chinh, khong cat xuyen cac khoi nha.
        Waypoints.Add(FVector(GetHero()->GetActorLocation().X, 1100, 100));
        Waypoints.Add(FVector(Destination.X, 1100, 100));
    }
    Waypoints.Add(Destination);
    NextPhase(ECityMissionCheckPhase::Route,
        FString::Printf(TEXT("Route to %s with ordinary W/Shift input"), *ObjectiveId().ToString()));
}

bool UCityMissionCheckSubsystem::WalkToward(const FVector& Destination, const float Tolerance)
{
    FVector Direction = Destination - GetHero()->GetActorLocation();
    Direction.Z = 0;
    const double Distance = Direction.Size();
    const bool bReached = Distance <= Tolerance;
    SetKey(EKeys::W, !bReached);
    SetKey(EKeys::S, false);
    SetKey(EKeys::LeftShift, !bReached && Distance > 450);
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
            Finish(false, TEXT("Held walking input is blocked for 12 seconds"));
        }
    }
    else
    {
        MotionOrigin = GetHero()->GetActorLocation();
        MotionTime = Now;
    }
    return bReached;
}

void UCityMissionCheckSubsystem::RunPhase()
{
    switch (Phase)
    {
    case ECityMissionCheckPhase::Route:
        if (WalkToward(Waypoints[Waypoint], 30))
        {
            Observe(true, FString::Printf(TEXT("Waypoint %d reached for %s"),
                Waypoint, *ObjectiveId().ToString()));
            if (++Waypoint == Waypoints.Num())
            {
                NextPhase(ECityMissionCheckPhase::Interact, TEXT("Reached target approach; awaiting settled E input"));
            }
        }
        break;
    case ECityMissionCheckPhase::Interact:
        RunInteraction();
        break;
    case ECityMissionCheckPhase::Fight:
        RunCombat();
        break;
    case ECityMissionCheckPhase::Repeat:
        if (!IsComplete(GetState()->GetProgress()))
        {
            Finish(false, TEXT("Completed mission or single reward was lost"));
            return;
        }
        if (!bInputSent && PhaseElapsed > 1)
        {
            const auto* Giver = FindItem(TEXT("Giver_Cafe"));
            FHitResult Hit;
            FCollisionQueryParams Params(SCENE_QUERY_STAT(CityMissionRepeat), false, GetHero());
            Params.AddIgnoredActor(Giver);
            if (!Giver || FVector::Dist(GetHero()->GetActorLocation(), Giver->GetActorLocation()) >= 320
                || GetWorld()->LineTraceSingleByChannel(Hit,
                    GetHero()->GetActorLocation() + FVector(0, 0, 40),
                    Giver->GetActorLocation() + FVector(0, 0, 40), ECC_Visibility, Params))
            {
                Finish(false, TEXT("Giver is not physically reachable for repeat E input"));
                return;
            }
            // Giver da hoan thanh khong con la target; E van phai giu nguyen mot thuong.
            TapKey(EKeys::E);
            bInputSent = true;
        }
        else if (bInputSent && PhaseElapsed > 1.6f)
        {
            NextPhase(ECityMissionCheckPhase::Save, TEXT("Repeated E beside giver preserved reward exactly one"));
        }
        break;
    case ECityMissionCheckPhase::Save:
        RunSave();
        break;
    default:
        break;
    }
}

void UCityMissionCheckSubsystem::RunInteraction()
{
    if (!bInputSent && PhaseElapsed > 1)
    {
        auto* Item = FindItem(ObjectiveId());
        if (!Item)
        {
            return;
        }
        if (Controller->FindInteractionTarget() != Item)
        {
            Finish(false, TEXT("Expected mission actor is not the ordinary E interaction target"));
            return;
        }
        TapKey(EKeys::E);
        bInputSent = true;
        return;
    }
    if (!bInputSent || PhaseElapsed < 1.6f)
    {
        return;
    }
    const auto& Mission = GetState()->GetMission();
    const ECityMissionStage Expected = Objective == 0 || Objective < 3 ? ECityMissionStage::Investigating
        : Objective == 3 ? ECityMissionStage::Combat
        : Objective == 4 ? ECityMissionStage::ReturnToGiver : ECityMissionStage::Completed;
    const bool bClue = Objective >= 1 && Objective <= 3;
    if (!Mission.IsValid() || Mission.Stage != Expected
        || (bClue && (!Mission.Clues.Contains(ObjectiveId()) || Mission.Clues.Num() != Objective)))
    {
        Finish(false, TEXT("E did not produce the expected stage and unique clue set"));
        return;
    }
    Observe(true, FString::Printf(TEXT("Normal E accepted %s"), *ObjectiveId().ToString()));
    if (Objective == 3)
    {
        NextPhase(ECityMissionCheckPhase::Fight, TEXT("Three unique clues activated normal enemy combat"));
    }
    else if (Objective == 5)
    {
        NextPhase(ECityMissionCheckPhase::Repeat, TEXT("Reported fragment and observed exactly one reward"));
    }
    else
    {
        ++Objective;
        BeginRoute();
    }
}

void UCityMissionCheckSubsystem::RunCombat()
{
    const auto& Mission = GetState()->GetMission();
    for (const FName Id : Mission.DefeatedEnemies)
    {
        if (!SeenActiveEnemies.Contains(Id))
        {
            Finish(false, TEXT("Defeat recorded without observing that enemy active in normal combat"));
            return;
        }
        if (!ObservedDefeats.Contains(Id))
        {
            ObservedDefeats.Add(Id);
            Observe(true, FString::Printf(TEXT("Observed defeat of %s through attack input"), *Id.ToString()));
        }
    }
    if (Mission.Stage != ECityMissionStage::Combat || !Mission.IsValid())
    {
        Finish(false, TEXT("Unexpected mission state during combat"));
        return;
    }
    if (Mission.DefeatedEnemies.Num() == 3)
    {
        Objective = 4;
        BeginRoute();
        return;
    }
    AANANTACityEnemy* Nearest = nullptr;
    double Distance = TNumericLimits<double>::Max();
    TSet<FName> LoadedIds;
    for (TActorIterator<AANANTACityEnemy> It(GetWorld()); It; ++It)
    {
        if (!FCityMissionState::IsEnemy(It->EnemyId))
        {
            continue;
        }
        if (LoadedIds.Contains(It->EnemyId))
        {
            Finish(false, TEXT("Duplicate loaded enemy ID"));
            return;
        }
        LoadedIds.Add(It->EnemyId);
        if (It->Health <= 0 || It->IsHidden() || Mission.DefeatedEnemies.Contains(It->EnemyId))
        {
            continue;
        }
        SeenActiveEnemies.Add(It->EnemyId);
        const double Candidate = FVector::Dist2D(GetHero()->GetActorLocation(), It->GetActorLocation());
        if (Candidate < Distance)
        {
            Nearest = *It;
            Distance = Candidate;
        }
    }
    if (!Nearest)
    {
        WalkToward(FVector(26000, 3800, 100), 40);
        return;
    }
    WalkToward(Nearest->GetActorLocation(), 240);
    if (bFinished)
    {
        return;
    }
    Controller->SetControlRotation(FRotator(-12,
        (Nearest->GetActorLocation() - GetHero()->GetActorLocation()).Rotation().Yaw, 0));
    // Lui bang S de giu tam danh, tranh dung yen cho nhieu dich vay danh.
    SetKey(EKeys::S, Distance < 215);
    const double GameTime = GetWorld()->GetTimeSeconds();
    if (Distance <= 240 && GameTime - LastAttackTime >= 0.72 && !HeldKeys.Contains(EKeys::LeftMouseButton))
    {
        TapKey(EKeys::LeftMouseButton);
        LastAttackTime = GameTime;
    }
}
