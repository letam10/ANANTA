#include "ANANTAHUD.h"

#include "Blueprint/UserWidget.h"
#include "Engine/World.h"
#include "UObject/ConstructorHelpers.h"

AANANTAHUD::AANANTAHUD()
{
    // Giữ đường dẫn asset ở một chỗ; GameMode Blueprint vẫn có thể override
    // class này cho các biến thể HUD về sau.
    static ConstructorHelpers::FClassFinder<UUserWidget> WidgetClass(
        TEXT("/Game/ANANTA/UI/WBP_NovaHUD"));
    if (WidgetClass.Succeeded())
    {
        NovaHUDClass = WidgetClass.Class;
    }
}

void AANANTAHUD::BeginPlay()
{
    Super::BeginPlay();

    if (!NovaHUDClass)
    {
        UE_LOG(LogTemp, Warning,
            TEXT("ANANTA HUD could not load /Game/ANANTA/UI/WBP_NovaHUD."));
        return;
    }

    if (UWorld* World = GetWorld())
    {
        NovaHUDWidget = CreateWidget<UUserWidget>(World, NovaHUDClass);
        if (NovaHUDWidget)
        {
            NovaHUDWidget->AddToViewport(100);
        }
    }
}
