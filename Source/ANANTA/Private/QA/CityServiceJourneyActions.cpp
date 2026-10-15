#include "QA/CityServiceJourney.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "City/CityServiceInteractable.h"
#include "Engine/World.h"
#include "EngineUtils.h"

ACityServiceInteractable* UCityServiceJourney::FindService() const
{
    ACityServiceInteractable* Result = nullptr;
    for (TActorIterator<ACityServiceInteractable> It(GetWorld()); It; ++It)
    {
        if (It->InteractionId == ServiceId(Venue))
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

bool UCityServiceJourney::MatchesProgress(const UANANTACitySave* Save, const int32 Visits) const
{
    if (!Save || !Save->IsValidSave() || !Save->LegacyFragments.IsEmpty())
    {
        return false;
    }
    const auto& Mission = Save->Mission;
    const auto& Services = Save->Services;
    if (Mission.Stage != ECityMissionStage::NotStarted || Mission.RewardCount != 0
        || Mission.bFragmentCollected || !Mission.Clues.IsEmpty() || !Mission.DefeatedEnemies.IsEmpty()
        || Services.VisitedIds.Num() != Visits || Services.SuppliesCount != (Visits >= 2 ? 1 : 0)
        || Services.ClaimedSupplyIds.Num() != Services.SuppliesCount
        || (Visits >= 2 && !Services.ClaimedSupplyIds.Contains(TEXT("Market_Supplies"))))
    {
        return false;
    }
    for (int32 Index = 0; Index < Visits; ++Index)
    {
        if (!Services.VisitedIds.Contains(ServiceId(Index)))
        {
            return false;
        }
    }
    return true;
}

void UCityServiceJourney::RunPhase()
{
    switch (Phase)
    {
    case ECityServiceJourneyPhase::Route:
        if (WalkToward(Waypoints[Waypoint]) && !bFinished)
        {
            if (++Waypoint == Waypoints.Num())
            {
                NextPhase(bLeavingLastVenue ? ECityServiceJourneyPhase::Save
                    : ECityServiceJourneyPhase::Interact, TEXT("Waypoint route reached using W and Shift"));
            }
        }
        break;
    case ECityServiceJourneyPhase::Interact:
        RunInteraction(false);
        break;
    case ECityServiceJourneyPhase::Repeat:
        RunInteraction(true);
        break;
    case ECityServiceJourneyPhase::Save:
        RunSave();
        break;
    case ECityServiceJourneyPhase::Reload:
        if (PhaseElapsed >= 2)
        {
            Finish(VerifyRestoredProgress(),
                TEXT("Separate process checkpoint, QA disk saves and live restore checked"));
        }
        break;
    default:
        break;
    }
}

void UCityServiceJourney::RunInteraction(const bool bRepeat)
{
    if (!bInputSent && PhaseElapsed >= 1)
    {
        auto* Service = FindService();
        if (!Service)
        {
            return;
        }
        if (Controller->FindInteractionTarget() != Service)
        {
            Finish(false, TEXT("Streamed service is not the ordinary controller E target"));
            return;
        }
        Observe(true, FString::Printf(TEXT("Unique streamed service=%s normal_target=1 repeat=%d prompt=%s"),
            *ServiceId(Venue).ToString(), bRepeat, *Controller->GetInteractionPrompt()));
        TapKey(EKeys::E);
        bInputSent = true;
        return;
    }
    if (!bInputSent || PhaseElapsed < 1.6)
    {
        return;
    }
    if (!MatchesProgress(GetState()->GetProgress(), Venue + 1))
    {
        Finish(false, TEXT("E did not retain exact visited IDs, one-time supply or untouched mission"));
        return;
    }
    if ((Venue == 0 || Venue == 3 || Venue == 4) && !FMath::IsNearlyEqual(GetHero()->Health, 100.f))
    {
        Finish(false, TEXT("Rest or clinic interaction did not leave full health"));
        return;
    }
    Observe(true, bRepeat ? TEXT("Repeated Market E preserved one supply and exact visits")
        : TEXT("Service E accepted; exact visited set verified"));
    if (Venue == 1 && !bRepeat)
    {
        NextPhase(ECityServiceJourneyPhase::Repeat, TEXT("Repeat Market claim through ordinary E"));
    }
    else if (Venue == 7)
    {
        BeginExit();
    }
    else
    {
        ++Venue;
        BeginRoute();
    }
}
