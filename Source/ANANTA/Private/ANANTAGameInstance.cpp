#include "ANANTAGameInstance.h"
#include "City/ANANTACitySubsystem.h"

UANANTAGameInstance::UANANTAGameInstance()
    : SessionVersion(1)
{
}

bool UANANTAGameInstance::RegisterFragment(const FName FragmentId)
{
    if (FragmentId.IsNone() || HasCollectedFragment(FragmentId))
    {
        return false;
    }

    const int32 PreviousCount = CollectedFragmentIds.Num();
    CollectedFragmentIds.Add(FragmentId);
    if (auto* State = GetSubsystem<UANANTACitySubsystem>())
    {
        State->RegisterLegacyFragment(FragmentId);
    }
    return CollectedFragmentIds.Num() > PreviousCount;
}

bool UANANTAGameInstance::HasCollectedFragment(const FName FragmentId) const
{
    const auto* State = GetSubsystem<UANANTACitySubsystem>();
    return !FragmentId.IsNone() && (CollectedFragmentIds.Contains(FragmentId)
        || (State && State->HasLegacyFragment(FragmentId)));
}

int32 UANANTAGameInstance::GetCollectedFragmentCount() const
{
    const auto* State = GetSubsystem<UANANTACitySubsystem>();
    return State ? State->GetProgress()->LegacyFragments.Num() : CollectedFragmentIds.Num();
}
