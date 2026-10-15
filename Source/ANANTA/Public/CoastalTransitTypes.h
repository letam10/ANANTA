#pragma once

#include "CoreMinimal.h"

UENUM(BlueprintType)
enum class ECoastalVehicleType : uint8
{
    Road,
    Emergency,
    Rowboat,
    Aircraft,
    Helicopter
};

UENUM(BlueprintType)
enum class ECoastalVehicleState : uint8
{
    Idle,
    Occupied,
    Moving,
    Rowing,
    Stopped,
    Blocked
};

UENUM(BlueprintType)
enum class ECoastalTransitFailureReason : uint8
{
    None,
    InvalidCharacter,
    AlreadyOccupied,
    CharacterTooFar,
    CharacterHasNoController,
    VehicleMoving,
    NoSafeExit,
    ExitBlocked,
    RouteBlocked,
    RouteLimit,
    SignalStop,
    NotStopped,
    NoPassenger,
    BoardingBlocked,
    ControlUnavailable
};

UENUM(BlueprintType)
enum class ECoastalTrainSignalState : uint8
{
    Clear,
    Caution,
    Stop
};

UENUM(BlueprintType)
enum class ECoastalTrainState : uint8
{
    Running,
    Stopped,
    Boarding,
    Alighting,
    Blocked
};
