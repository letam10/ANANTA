#include "CoastalQA.h"

#include "CoastalCharacter.h"
#include "CoastalInteractable.h"
#include "CoastalTrain.h"
#include "CoastalVehicle.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "InputKeyEventArgs.h"

namespace
{
    FVector ScheduledOrigin = FVector::ZeroVector;
    bool bScheduledOriginCaptured = false;
}

void ACoastalQA::Key(const FKey& KeyName, bool Pressed)
{
    GetWorld()->GetFirstPlayerController()->InputKey(FInputKeyEventArgs(nullptr,
        FInputDeviceId::CreateFromInternalId(0), KeyName, Pressed ? IE_Pressed : IE_Released,
        1, false, FPlatformTime::Cycles64()));
}

void ACoastalQA::TestInteractions()
{
    int32 Doors = 0;
    int32 ClearDoors = 0;
    int32 Services = 0;
    int32 Citizens = 0;
    int32 Items = 0;
    int32 ScheduledCitizens = 0;
    int32 SmallProps = 0;
    int32 Signals = 0;
    int32 SignalStates = 0;
    int32 Trains = 0;
    int32 EastboundTrains = 0;
    int32 WestboundTrains = 0;
    int32 InteractionRecords = 0;
    int32 NormalizedInteractions = 0;
    bool bFailureResponse = false;
    ACoastalInteractable* FirstDoor = nullptr;
    for (TActorIterator<ACoastalInteractable> It(GetWorld()); It; ++It)
    {
        ++InteractionRecords;
        const bool bNormalized = !It->GetVenueId().IsNone()
            && !It->GetPropId().IsNone()
            && !It->GetInteractionSaveKey().IsNone()
            && !It->GetInteractionPrompt().IsEmpty()
            && !It->FailureMessage.IsEmpty();
        NormalizedInteractions += bNormalized ? 1 : 0;
        if (!bFailureResponse)
        {
            bFailureResponse = !It->ReportInteractionFailure(TEXT("QA bounded failure path")).IsEmpty();
        }
        if (It->Kind == 1)
        {
            ++Doors;
            FVector Center = It->Mesh->Bounds.Origin;
            Center.Z = It->GetActorLocation().Z + 100;
            FHitResult Closed;
            FCollisionQueryParams Query(SCENE_QUERY_STAT(CoastalDoorQA), false, Player);
            const FVector Start = Center - FVector(0, 180, 0);
            const FVector End = Center + FVector(0, 180, 0);
            const bool Blocks = GetWorld()->LineTraceSingleByChannel(Closed, Start, End, ECC_Visibility, Query);
            It->Use();
            FHitResult Open;
            const bool OpenBlocks = GetWorld()->LineTraceSingleByChannel(Open, Start, End, ECC_Visibility, Query);
            ClearDoors += Blocks && Closed.GetActor() == *It && !OpenBlocks ? 1 : 0;
            It->Use();
            FirstDoor = FirstDoor ? FirstDoor : *It;
        }
        else if (It->Kind == 3)
        {
            It->Use();
            Items += It->bUsed && !It->Mesh->IsVisible() ? 1 : 0;
            Check(TEXT("pickup_not_duplicated"), It->Use() == TEXT("Already collected"));
        }
        else if (It->Kind == 2)
        {
            Citizens += !It->Use().IsEmpty() && It->bUsed ? 1 : 0;
            if (It->bScheduleEnabled)
            {
                ++ScheduledCitizens;
                if (!bScheduledOriginCaptured)
                {
                    ScheduledOrigin = It->GetActorLocation();
                    bScheduledOriginCaptured = true;
                }
            }
        }
        else if (It->Kind == 0)
        {
            Services += !It->Use().IsEmpty() && It->bUsed ? 1 : 0;
        }
        else if (It->Kind == 6)
        {
            ++Signals;
            SignalStates += It->SignalState >= 0 && It->SignalState <= 2 ? 1 : 0;
        }
        else if (It->Kind == 4)
        {
            FCollisionQueryParams Query(SCENE_QUERY_STAT(CoastalLiftQA), false, Player);
            Query.AddIgnoredActor(*It);
            Check(TEXT("lift_landing_clear"), !GetWorld()->OverlapBlockingTestByChannel(
                It->Destination, FQuat::Identity, ECC_Pawn, FCollisionShape::MakeCapsule(34, 90), Query));
        }
        else if (It->Kind == 5)
        {
            const FString Response = It->Use();
            SmallProps += !Response.IsEmpty() && It->bUsed ? 1 : 0;
        }
    }
    for (TActorIterator<ACoastalTrain> It(GetWorld()); It; ++It)
    {
        ++Trains;
        EastboundTrains += It->Direction > 0 ? 1 : 0;
        WestboundTrains += It->Direction < 0 ? 1 : 0;
    }
    Check(TEXT("all_23_doorways_close_and_clear_on_open"), Doors == 23 && ClearDoors == Doors);
    Check(TEXT("23_services_respond"), Services >= 23);
    Check(TEXT("23_npcs_respond"), Citizens == 23);
    Check(TEXT("23_npcs_scheduled"), ScheduledCitizens == 23);
    Check(TEXT("5_items_collect"), Items == 5);
    Check(TEXT("micro_props_respond"), SmallProps >= 5);
    Check(TEXT("11_micro_props_present"), SmallProps >= 11);
    Check(TEXT("traffic_signals_present"), Signals >= 20 && SignalStates == Signals);
    Check(TEXT("train_two_way_present"), Trains == 2 && EastboundTrains == 1 && WestboundTrains == 1);
    Check(TEXT("interaction_data_normalized"), InteractionRecords > 0
        && NormalizedInteractions == InteractionRecords);
    Check(TEXT("interaction_failure_message"), bFailureResponse);
    TestTransit();
    if (FirstDoor)
    {
        FVector Position = FirstDoor->Mesh->Bounds.Origin - FVector(0, 190, 0);
        Position.Z = 296;
        Player->SetActorLocation(Position);
        Check(TEXT("door_selected_from_street"), Player->FindAction() == FirstDoor);
        Key(EKeys::E, true);
    }
    FHitResult Border;
    Check(TEXT("ocean_boundary_blocks"), GetWorld()->LineTraceSingleByChannel(Border,
        FVector(71500, 0, 1000), FVector(72500, 0, 1000), ECC_Visibility));
}

void ACoastalQA::TestTransit()
{
    int32 Aircraft = 0;
    int32 Helicopters = 0;
    int32 BoundedVehicles = 0;
    for (TActorIterator<ACoastalVehicle> It(GetWorld()); It; ++It)
    {
        const ECoastalVehicleType Type = It->GetVehicleType();
        Aircraft += Type == ECoastalVehicleType::Aircraft ? 1 : 0;
        Helicopters += Type == ECoastalVehicleType::Helicopter ? 1 : 0;
        BoundedVehicles += It->bRouteBounded ? 1 : 0;
    }
    Check(TEXT("aircraft_and_heli_control_states"), Aircraft >= 1 && Helicopters >= 1);
    Check(TEXT("vehicle_route_bounds_authored"), BoundedVehicles >= 5);

    int32 SignalStops = 0;
    int32 SignalReleases = 0;
    int32 DirectionMatches = 0;
    int32 Boarded = 0;
    int32 Alighted = 0;
    for (TActorIterator<ACoastalTrain> It(GetWorld()); It; ++It)
    {
        const FVector Forward = It->GetActorForwardVector();
        DirectionMatches += It->Direction * Forward.X > 0 ? 1 : 0;
        It->SetSignalState(ECoastalTrainSignalState::Stop);
        SignalStops += It->IsStopped() && It->GetTrainState() == ECoastalTrainState::Blocked ? 1 : 0;
        It->SetSignalState(ECoastalTrainSignalState::Clear);
        It->HoldAtStationForBoarding();
        SignalReleases += It->IsStopped() ? 1 : 0;
        if (Player)
        {
            Player->SetActorLocation(It->GetActorLocation() + It->GetActorRightVector() * 300);
            const bool bBoarded = It->Board(Player);
            Boarded += bBoarded ? 1 : 0;
            const bool bAlighted = bBoarded && It->Alight();
            Alighted += bAlighted ? 1 : 0;
        }
    }
    Check(TEXT("train_signal_stop"), SignalStops == 2);
    Check(TEXT("train_signal_release_and_station_stop"), SignalReleases == 2);
    Check(TEXT("train_transform_direction"), DirectionMatches == 2);
    Check(TEXT("train_boarding"), Boarded == 2);
    Check(TEXT("train_alighting"), Alighted == Boarded);
}

bool ACoastalQA::AdvanceGameplayTests()
{
    APlayerController* Controller = GetWorld()->GetFirstPlayerController();
    const double Age = GetWorld()->GetTimeSeconds() - PhaseStarted;
    auto Advance = [this]()
    {
        ++Phase;
        PhaseStarted = GetWorld()->GetTimeSeconds();
    };
    if (Phase == 0 && Age > 3)
    {
        TestInteractions();
        Advance();
    }
    else if (Phase == 1 && Age > 0.4)
    {
        Key(EKeys::E, false);
        bool bScheduleMoved = false;
        for (TActorIterator<ACoastalInteractable> It(GetWorld()); It; ++It)
        {
            if (It->Kind == 2 && It->bScheduleEnabled)
            {
                bScheduleMoved = FVector::Dist2D(ScheduledOrigin, It->GetActorLocation()) > 1.0f;
                break;
            }
        }
        Check(TEXT("npc_schedule_moves"), bScheduledOriginCaptured && bScheduleMoved);
        int32 Opened = 0;
        for (TActorIterator<ACoastalInteractable> It(GetWorld()); It; ++It)
        {
            if (It->Kind == 1 && It->bUsed)
            {
                ++Opened;
                It->Use();
            }
        }
        Check(TEXT("E_key_opens_door"), Opened == 1);
        Player->SetActorLocation(FVector(-4800, -3200, 296));
        Controller->SetControlRotation(FRotator::ZeroRotator);
        StartVehiclePosition = Player->GetActorLocation();
        Key(EKeys::W, true);
        Advance();
    }
    else if (Phase == 2 && Age > 0.85)
    {
        Key(EKeys::W, false);
        Check(TEXT("W_key_walks_character"), FVector::Dist2D(StartVehiclePosition, Player->GetActorLocation()) > 150);
        for (TActorIterator<ACoastalVehicle> It(GetWorld()); It; ++It)
        {
            if (!It->bBoat && (It->GetVehicleType() == ECoastalVehicleType::Road
                || It->GetVehicleType() == ECoastalVehicleType::Emergency))
            {
                TestVehicle = *It;
                break;
            }
        }
        Check(TEXT("service_vehicle_exists"), TestVehicle != nullptr);
        if (!TestVehicle)
        {
            return true;
        }
        SavedVehicleTransform = TestVehicle->GetActorTransform();
        Player->SetActorLocation(TestVehicle->GetActorLocation() + TestVehicle->GetActorRightVector() * 250);
        Check(TEXT("vehicle_board"), TestVehicle->Board(Player));
        StartVehiclePosition = TestVehicle->GetActorLocation();
        Key(EKeys::W, true);
        Advance();
    }
    else if (Phase == 3 && Age > 1)
    {
        Key(EKeys::W, false);
        Check(TEXT("W_key_drives_vehicle"), FVector::Dist2D(StartVehiclePosition, TestVehicle->GetActorLocation()) > 120);
        Advance();
    }
    else if (Phase == 4 && Age > 2.2)
    {
        const bool LeftVehicle = TestVehicle->Leave();
        Check(TEXT("vehicle_safe_exit"), LeftVehicle && Controller->GetPawn() == Player);
        if (!LeftVehicle)
        {
            return true;
        }
        TestVehicle->SetActorTransform(SavedVehicleTransform);
        for (TActorIterator<ACoastalVehicle> It(GetWorld()); It; ++It)
        {
            if (It->bBoat)
            {
                TestVehicle = *It;
                break;
            }
        }
        Player->SetActorLocation(FVector(21100, -11500, 177));
        Check(TEXT("rowboat_board_at_pier"), TestVehicle->Board(Player));
        StartVehiclePosition = TestVehicle->GetActorLocation();
        Key(EKeys::W, true);
        Advance();
    }
    else if (Phase == 5 && Age > 0.8)
    {
        Key(EKeys::W, false);
        Check(TEXT("W_key_rows_boat"), FVector::Dist2D(StartVehiclePosition, TestVehicle->GetActorLocation()) > 40);
        Advance();
    }
    else if (Phase == 6 && Age > 2.5)
    {
        Check(TEXT("rowboat_safe_exit_on_dock"), TestVehicle->Leave() && Controller->GetPawn() == Player);
        return true;
    }
    return false;
}
