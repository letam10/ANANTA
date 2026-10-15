#include "City/ANANTACityState.h"
#include "City/CityWorldBounds.h"

bool FCityMissionState::IsClue(const FName Id)
{
    return Id == TEXT("Clue_01") || Id == TEXT("Clue_02") || Id == TEXT("Clue_03");
}

bool FCityMissionState::IsEnemy(const FName Id)
{
    return Id == TEXT("Enemy_01") || Id == TEXT("Enemy_02") || Id == TEXT("Enemy_03");
}

bool FCityMissionState::Interact(const FName Id, const ECityInteractionKind Kind)
{
    if (Kind == ECityInteractionKind::Giver && Id == TEXT("Giver_Cafe"))
    {
        if (Stage == ECityMissionStage::NotStarted)
        {
            Stage = ECityMissionStage::Investigating;
            return true;
        }
        if (Stage == ECityMissionStage::ReturnToGiver && bFragmentCollected && RewardCount == 0)
        {
            Stage = ECityMissionStage::Completed;
            RewardCount = 1;
            return true;
        }
    }
    if (Kind == ECityInteractionKind::Clue && Stage == ECityMissionStage::Investigating
        && IsClue(Id) && !Clues.Contains(Id))
    {
        Clues.Add(Id);
        if (Clues.Num() == 3)
        {
            Stage = ECityMissionStage::Combat;
        }
        return true;
    }
    if (Kind == ECityInteractionKind::Fragment && Id == TEXT("Fragment_Anomaly")
        && Stage == ECityMissionStage::Combat && DefeatedEnemies.Num() == 3 && !bFragmentCollected)
    {
        bFragmentCollected = true;
        Stage = ECityMissionStage::ReturnToGiver;
        return true;
    }
    return false;
}

bool FCityMissionState::Defeat(const FName Id)
{
    if (Stage != ECityMissionStage::Combat || !IsEnemy(Id) || DefeatedEnemies.Contains(Id))
    {
        return false;
    }
    DefeatedEnemies.Add(Id);
    return true;
}

bool FCityMissionState::IsValid() const
{
    for (const FName Id : Clues)
    {
        if (!IsClue(Id))
        {
            return false;
        }
    }
    for (const FName Id : DefeatedEnemies)
    {
        if (!IsEnemy(Id))
        {
            return false;
        }
    }
    switch (Stage)
    {
    case ECityMissionStage::NotStarted:
        return Clues.IsEmpty() && DefeatedEnemies.IsEmpty() && !bFragmentCollected && RewardCount == 0;
    case ECityMissionStage::Investigating:
        return Clues.Num() < 3 && DefeatedEnemies.IsEmpty() && !bFragmentCollected && RewardCount == 0;
    case ECityMissionStage::Combat:
        return Clues.Num() == 3 && !bFragmentCollected && RewardCount == 0;
    case ECityMissionStage::ReturnToGiver:
        return Clues.Num() == 3 && DefeatedEnemies.Num() == 3 && bFragmentCollected && RewardCount == 0;
    case ECityMissionStage::Completed:
        return Clues.Num() == 3 && DefeatedEnemies.Num() == 3 && bFragmentCollected && RewardCount == 1;
    default:
        return false;
    }
}

bool UANANTACitySave::IsValidSave() const
{
    const auto SafeTransform = [](const FTransform& Transform)
    {
        const FVector Position = Transform.GetLocation();
        return !Transform.ContainsNaN() && FMath::Abs(Position.X) <= CityWorldBounds::SaveExtent
            && FMath::Abs(Position.Y) <= CityWorldBounds::SaveExtent && Position.Z > -1000 && Position.Z < 30000;
    };
    return SchemaVersion == 1 && Mission.IsValid() && Services.IsValid()
        && (!bHasPlayerTransform || SafeTransform(PlayerTransform))
        && (!bHasCarTransform || SafeTransform(CarTransform));
}
