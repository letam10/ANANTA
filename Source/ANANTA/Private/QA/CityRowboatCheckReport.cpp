#include "QA/CityRowboatCheck.h"

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

const TCHAR* UCityRowboatCheck::PhaseName() const
{
    static const TCHAR* Names[] = {
        TEXT("WaitReady"), TEXT("Settle"), TEXT("Board"), TEXT("Row"),
        TEXT("Brake"), TEXT("Alight"), TEXT("OpenSea"), TEXT("Done")
    };
    return Names[static_cast<uint8>(Phase)];
}

void UCityRowboatCheck::Finish(const bool bSuccess, const FString& Reason)
{
    if (bFinished)
    {
        return;
    }
    bFinished = true;
    ReleaseKeys();
    bCapsule &= CheckCapsule();
    bPassed = bSuccess && bQASlot && bStreamed && bCapsule && bBoard && bRowInput && bBrakeInput
        && bBrake && bAlight && bCapsuleClear && bDryFloor && bOpenSeaSetup && bOpenSeaExitRejected
        && MeasuredTravelCm > 20 && RowDisplacementCm > 20 && RowSeconds >= 1 && StoppedSpeedKmh <= 0.05;
    FCityRowboatPhaseResult& FinalResult = Results.AddDefaulted_GetRef();
    FinalResult.Phase = PhaseName();
    FinalResult.Status = bPassed ? TEXT("PASS") : TEXT("FAIL");
    FinalResult.Reason = Reason;
    FinalResult.ElapsedSeconds = FPlatformTime::Seconds() - PhaseAt;

    const TSharedRef<FJsonObject> Report = MakeShared<FJsonObject>();
    Report->SetNumberField(TEXT("schemaVersion"), 1);
    Report->SetBoolField(TEXT("passed"), bPassed);
    Report->SetStringField(TEXT("completedUtc"), FDateTime::UtcNow().ToIso8601());
    Report->SetStringField(TEXT("scope"), TEXT("authored-map player rowboat input"));
    Report->SetStringField(TEXT("map"), GetWorld()->GetMapName());
    Report->SetStringField(TEXT("reason"), Reason);
    Report->SetStringField(TEXT("inputSource"), TEXT("PlayerController.InputKey E/W/Space/E"));
    Report->SetStringField(TEXT("authoredBoat"), TEXT("Living_PlayerRowboat"));
    Report->SetStringField(TEXT("boardPrompt"), BoardPrompt);
    Report->SetStringField(TEXT("alightPrompt"), AlightPrompt);
    Report->SetBoolField(TEXT("isolatedQASlot"), bQASlot);
    Report->SetBoolField(TEXT("streamingReady"), bStreamed);
    Report->SetNumberField(TEXT("streamingRadiusCm"), 30000);
    Report->SetNumberField(TEXT("elapsedSeconds"), FPlatformTime::Seconds() - StartedAt);
    Report->SetNumberField(TEXT("measuredTravelCm"), MeasuredTravelCm);
    Report->SetNumberField(TEXT("rowDisplacementCm"), RowDisplacementCm);
    Report->SetNumberField(TEXT("rowSeconds"), RowSeconds);
    Report->SetNumberField(TEXT("peakSpeedKmh"), PeakSpeedKmh);
    Report->SetNumberField(TEXT("brakeStartSpeedKmh"), BrakeStartSpeedKmh);
    Report->SetNumberField(TEXT("stoppedSpeedKmh"), StoppedSpeedKmh);
    Report->SetBoolField(TEXT("board"), bBoard);
    Report->SetBoolField(TEXT("rowInput"), bRowInput);
    Report->SetBoolField(TEXT("brakeInput"), bBrakeInput);
    Report->SetBoolField(TEXT("brake"), bBrake);
    Report->SetBoolField(TEXT("alight"), bAlight);
    Report->SetBoolField(TEXT("dryFloor"), bDryFloor);
    Report->SetBoolField(TEXT("openSeaExitRejected"), bOpenSeaExitRejected);
    Report->SetBoolField(TEXT("openSeaSetupRelocatedBoat"), bOpenSeaSetup);
    Report->SetBoolField(TEXT("openSeaRelocationIncludedInTravel"), false);
    Report->SetBoolField(TEXT("artificialSupportFloors"), false);
    Report->SetBoolField(TEXT("boatSpeedModified"), false);
    Report->SetBoolField(TEXT("collisionBypassDuringMeasurement"), false);
    const TSharedRef<FJsonObject> Capsule = MakeShared<FJsonObject>();
    Capsule->SetNumberField(TEXT("radiusCm"), CapsuleRadius);
    Capsule->SetNumberField(TEXT("halfHeightCm"), CapsuleHalfHeight);
    Capsule->SetBoolField(TEXT("unchanged"), bCapsule);
    Capsule->SetBoolField(TEXT("clearAfterAlight"), bCapsuleClear);
    Report->SetObjectField(TEXT("capsule"), Capsule);
    TArray<TSharedPtr<FJsonValue>> Phases;
    for (const FCityRowboatPhaseResult& Result : Results)
    {
        const TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
        Row->SetStringField(TEXT("phase"), Result.Phase);
        Row->SetStringField(TEXT("status"), Result.Status);
        Row->SetStringField(TEXT("reason"), Result.Reason);
        Row->SetNumberField(TEXT("elapsedSeconds"), Result.ElapsedSeconds);
        Phases.Add(MakeShared<FJsonValueObject>(Row));
    }
    Report->SetArrayField(TEXT("phases"), Phases);
    FString Json;
    const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Json);
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("QA/CityRowboatCheck");
    IFileManager::Get().MakeDirectory(*Directory, true);
    if (!FJsonSerializer::Serialize(Report, Writer)
        || !FFileHelper::SaveStringToFile(Json, *(Directory / TEXT("Report.json"))))
    {
        bPassed = false;
    }
    Phase = ECityRowboatPhase::Done;
    UE_LOG(LogTemp, Display, TEXT("CITY_ROWBOAT_CHECK_FINISH success=%d reason=%s"), bPassed, *Reason);
}
