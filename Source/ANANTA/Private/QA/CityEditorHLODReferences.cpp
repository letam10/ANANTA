#include "QA/CityEditorTools.h"

#if WITH_EDITOR
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "WorldPartition/HLOD/HLODActor.h"
#include "WorldPartition/HLOD/HLODSourceActorsFromCell.h"
#endif

FString UCityEditorTools::HLODSourceActorReferences(AActor* Actor)
{
#if WITH_EDITOR
    const auto* HLOD = Cast<AWorldPartitionHLOD>(Actor);
    const auto* Source = HLOD ? Cast<UWorldPartitionHLODSourceActorsFromCell>(HLOD->GetSourceActors()) : nullptr;
    auto Report = MakeShared<FJsonObject>();
    const bool bAvailable = Source && !Source->GetActors().IsEmpty();
    Report->SetBoolField(TEXT("available"), bAvailable);
    Report->SetStringField(TEXT("reason"),
        bAvailable ? TEXT("Cell source metadata") : TEXT("Missing cell metadata"));
    TArray<TSharedPtr<FJsonValue>> References;
    if (bAvailable)
    {
        // Doc mapping goc qua getter C++; khong can Python truy cap UPROPERTY private.
        for (const auto& Mapping : Source->GetActors())
        {
            auto Reference = MakeShared<FJsonObject>();
            Reference->SetStringField(TEXT("path"), Mapping.Path.ToString());
            Reference->SetStringField(TEXT("guid"), Mapping.ActorInstanceGuid.ToString());
            References.Add(MakeShared<FJsonValueObject>(Reference));
        }
    }
    Report->SetArrayField(TEXT("references"), References);
    FString Contents;
    FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Contents));
    return Contents;
#else
    return TEXT("{\"available\":false,\"reason\":\"Editor only\",\"references\":[]}");
#endif
}
