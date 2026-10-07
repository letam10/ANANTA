#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "CityEditorTools.generated.h"

class ARecastNavMesh;

UCLASS()
class ANANTA_API UCityEditorTools : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "City Editor", meta = (DevelopmentOnly))
    static ARecastNavMesh* EnsureNavigation(UWorld* World);
};
