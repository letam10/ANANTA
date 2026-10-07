#include "ANANTAGameInstance.h"

UANANTAGameInstance::UANANTAGameInstance()
    : SessionVersion(1)
{
}

bool UANANTAGameInstance::RegisterFragment(const FName FragmentId)
{
    if (FragmentId.IsNone())
    {
        return false;
    }

    const int32 PreviousCount = CollectedFragmentIds.Num();
    CollectedFragmentIds.Add(FragmentId);
    return CollectedFragmentIds.Num() > PreviousCount;
}

bool UANANTAGameInstance::HasCollectedFragment(const FName FragmentId) const
{
    return !FragmentId.IsNone() && CollectedFragmentIds.Contains(FragmentId);
}

int32 UANANTAGameInstance::GetCollectedFragmentCount() const
{
    return CollectedFragmentIds.Num();
}
