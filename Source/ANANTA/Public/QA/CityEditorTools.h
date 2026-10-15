#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "CityEditorTools.generated.h"

class ARecastNavMesh;
class AActor;
class UHierarchicalInstancedStaticMeshComponent;

UCLASS()
class ANANTA_API UCityEditorTools : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "City Editor", meta = (DevelopmentOnly))
    static ARecastNavMesh* EnsureNavigation(UWorld* World);

    UFUNCTION(BlueprintCallable, Category = "City Editor", meta = (DevelopmentOnly))
    static FString AuditLoadedCollision(UWorld* World);

    UFUNCTION(BlueprintCallable, Category = "City Editor", meta = (DevelopmentOnly))
    static FString AuditCollisionActors(UWorld* World, const TArray<FGuid>& ActorGuids);

    UFUNCTION(BlueprintCallable, Category = "City Editor", meta = (DevelopmentOnly))
    static FString AuditRoadRegion(UWorld* World, FVector Minimum, FVector Maximum);

    UFUNCTION(BlueprintCallable, Category = "City Editor", meta = (DevelopmentOnly))
    static FString AuditWorldBoundaries(UWorld* World, double ExtentCm);

    UFUNCTION(BlueprintCallable, Category = "City Editor", meta = (DevelopmentOnly))
    static FString FinalizeInstanceCollision(UHierarchicalInstancedStaticMeshComponent* Component);

    UFUNCTION(BlueprintCallable, Category = "City Editor", meta = (DevelopmentOnly))
    static FString HLODSourceActorReferences(AActor* Actor);
};
