#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "ANANTAGameInstance.generated.h"

UCLASS(Blueprintable)
class ANANTA_API UANANTAGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    UANANTAGameInstance();

    UFUNCTION(BlueprintCallable, Category = "ANANTA|Fragments")
    bool RegisterFragment(FName FragmentId);

    UFUNCTION(BlueprintPure, Category = "ANANTA|Fragments")
    bool HasCollectedFragment(FName FragmentId) const;

    UFUNCTION(BlueprintPure, Category = "ANANTA|Fragments")
    int32 GetCollectedFragmentCount() const;

    UPROPERTY(BlueprintReadOnly, VisibleAnywhere, Category = "Session")
    int32 SessionVersion;

private:
    UPROPERTY(BlueprintReadOnly, VisibleAnywhere, Category = "ANANTA|Fragments", meta = (AllowPrivateAccess = "true"))
    TSet<FName> CollectedFragmentIds;
};
