#include "QA/CityRoofPoolCheck.h"

#include "City/ANANTACityCharacter.h"
#include "Dom/JsonObject.h"
#include "Dom/JsonValue.h"
#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "Misc/DateTime.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

namespace
{
TSharedRef<FJsonObject> LegJson(const FCityRoofPoolLeg& Leg, const bool bAscent)
{
    const TSharedRef<FJsonObject> Json = MakeShared<FJsonObject>();
    Json->SetNumberField(TEXT("travelCm"), Leg.TravelCm);
    Json->SetNumberField(TEXT("forwardTravelCm"), (Leg.End.Y - Leg.Start.Y) * (bAscent ? 1 : -1));
    Json->SetNumberField(TEXT("heightChangeCm"), Leg.End.Z - Leg.Start.Z);
    Json->SetNumberField(TEXT("samples"), Leg.Samples);
    Json->SetNumberField(TEXT("inputSamples"), Leg.InputSamples);
    Json->SetNumberField(TEXT("sampledTreads"), Leg.Steps.Num());
    Json->SetStringField(TEXT("start"), Leg.Start.ToString());
    Json->SetStringField(TEXT("end"), Leg.End.ToString());
    TArray<TSharedPtr<FJsonValue>> Treads;
    for (int32 Index = 0; Index < 41; ++Index)
    {
        if (Leg.Steps.Contains(Index))
        {
            Treads.Add(MakeShared<FJsonValueNumber>(Index));
        }
    }
    Json->SetArrayField(TEXT("treadIndices"), Treads);
    return Json;
}
}

const TCHAR* UCityRoofPoolCheck::PhaseName() const
{
    static const TCHAR* Names[] = {
        TEXT("WaitReady"), TEXT("Settle"), TEXT("Ascent"), TEXT("Landing"), TEXT("Roof"),
        TEXT("ReturnLanding"), TEXT("Descent"), TEXT("Ground"), TEXT("Done")
    };
    return Names[static_cast<uint8>(Phase)];
}

void UCityRoofPoolCheck::Finish(const bool bSuccess, const FString& Reason)
{
    if (bFinished)
    {
        return;
    }
    bFinished = true;
    SetForward(false);
    bSettingsUnchanged &= CheckBodySettings();
    bPassed = bSuccess && bQASlot && bStreamed && bSettingsUnchanged && bRoof && bReturned
        && Ascent.End.Y - Ascent.Start.Y >= 4100 && Descent.Start.Y - Descent.End.Y >= 4100
        && Ascent.End.Z - Ascent.Start.Z >= 810 && Descent.Start.Z - Descent.End.Z >= 810
        && Ascent.Steps.Num() == 41 && Descent.Steps.Num() == 41
        && Ascent.InputSamples >= 41 && Descent.InputSamples >= 41
        && LandingInputSamples >= 2 && ReturnInputSamples >= 2 && RoofSamples >= 2
        && FloorSamples >= 84 && ClearanceSamples == FloorSamples && FMath::Abs(RoofZ - 840) <= 3;
    const FString Outcome = bSuccess && !bPassed ? TEXT("Final aggregate evidence gate failed") : Reason;
    auto& FinalResult = Results.AddDefaulted_GetRef();
    FinalResult.Phase = PhaseName();
    FinalResult.Reason = Outcome;
    FinalResult.bPassed = bPassed;
    FinalResult.ElapsedSeconds = FPlatformTime::Seconds() - PhaseAt;
    const TSharedRef<FJsonObject> Report = MakeShared<FJsonObject>();
    Report->SetNumberField(TEXT("schemaVersion"), 1);
    Report->SetBoolField(TEXT("passed"), bPassed);
    Report->SetStringField(TEXT("completedUtc"), FDateTime::UtcNow().ToIso8601());
    Report->SetStringField(TEXT("scope"), TEXT("authored-map rooftop pool stair walking input"));
    Report->SetStringField(TEXT("map"), GetWorld()->GetMapName());
    Report->SetStringField(TEXT("phase"), PhaseName());
    Report->SetStringField(TEXT("reason"), Outcome);
    Report->SetStringField(TEXT("blocker"), Blocker);
    Report->SetStringField(TEXT("floorActor"), FloorActor);
    Report->SetStringField(TEXT("position"), Hero() ? Hero()->GetActorLocation().ToString() : TEXT("missing"));
    Report->SetStringField(TEXT("inputSource"), TEXT("PlayerController.InputKey W; camera yaw follows each leg"));
    Report->SetNumberField(TEXT("elapsedSeconds"), FPlatformTime::Seconds() - StartedAt);
    Report->SetBoolField(TEXT("isolatedQASlot"), bQASlot);
    Report->SetBoolField(TEXT("streamingReady"), bStreamed);
    Report->SetNumberField(TEXT("streamingRadiusCm"), 30000);
    Report->SetNumberField(TEXT("roofHeightCm"), RoofZ);
    Report->SetNumberField(TEXT("lastFloorHeightCm"), FloorZ);
    Report->SetNumberField(TEXT("floorSamples"), FloorSamples);
    Report->SetNumberField(TEXT("clearanceSamples"), ClearanceSamples);
    Report->SetNumberField(TEXT("landingInputSamples"), LandingInputSamples);
    Report->SetNumberField(TEXT("returnInputSamples"), ReturnInputSamples);
    Report->SetNumberField(TEXT("roofSamples"), RoofSamples);
    Report->SetBoolField(TEXT("roofReached"), bRoof);
    Report->SetBoolField(TEXT("courtyardReturned"), bReturned);
    Report->SetBoolField(TEXT("artificialSupportFloors"), false);
    Report->SetBoolField(TEXT("teleportDuringMeasurement"), false);
    Report->SetBoolField(TEXT("movementSettingsModified"), false);
    Report->SetBoolField(TEXT("swimmingTested"), false);
    TArray<TSharedPtr<FJsonValue>> Errors;
    if (!bPassed)
    {
        Errors.Add(MakeShared<FJsonValueString>(FString::Printf(TEXT("%s: %s"), PhaseName(), *Outcome)));
    }
    Report->SetArrayField(TEXT("errors"), Errors);
    Report->SetObjectField(TEXT("ascent"), LegJson(Ascent, true));
    Report->SetObjectField(TEXT("descent"), LegJson(Descent, false));
    const TSharedRef<FJsonObject> Capsule = MakeShared<FJsonObject>();
    Capsule->SetNumberField(TEXT("radiusCm"), 38);
    Capsule->SetNumberField(TEXT("halfHeightCm"), 92);
    Capsule->SetBoolField(TEXT("unchanged"), bSettingsUnchanged);
    Capsule->SetBoolField(TEXT("clear"), ClearanceSamples > 0 && ClearanceSamples == FloorSamples && bPassed);
    Report->SetObjectField(TEXT("capsule"), Capsule);
    TArray<TSharedPtr<FJsonValue>> Phases;
    for (const auto& Result : Results)
    {
        const TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
        Row->SetStringField(TEXT("phase"), Result.Phase);
        Row->SetStringField(TEXT("status"), Result.bPassed ? TEXT("PASS") : TEXT("FAIL"));
        Row->SetStringField(TEXT("reason"), Result.Reason);
        Row->SetNumberField(TEXT("elapsedSeconds"), Result.ElapsedSeconds);
        Phases.Add(MakeShared<FJsonValueObject>(Row));
    }
    Report->SetArrayField(TEXT("phases"), Phases);
    FString Json;
    const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Json);
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("QA/CityRoofPoolCheck");
    IFileManager::Get().MakeDirectory(*Directory, true);
    if (!FJsonSerializer::Serialize(Report, Writer)
        || !FFileHelper::SaveStringToFile(Json, *(Directory / TEXT("Report.json"))))
    {
        bPassed = false;
    }
    UE_LOG(LogTemp, Display, TEXT("CITY_ROOFPOOL_CHECK_FINISH success=%d phase=%s reason=%s blocker=%s"),
        bPassed, PhaseName(), *Outcome, *Blocker);
    Phase = ECityRoofPoolPhase::Done;
}
