#include "Settings/SCitySettingsPanel.h"

#include "Styling/CoreStyle.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"

TSharedRef<SWidget> SCitySettingsPanel::BuildLayout()
{
    const TSharedRef<SVerticalBox> Rows = SNew(SVerticalBox);
    AddGraphicsControls(Rows);
    AddDisplayControls(Rows);
    return SNew(SBorder)
        .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
        .BorderBackgroundColor(FLinearColor(0.004f, 0.009f, 0.022f, 0.96f))
        .Padding(FMargin(28.f, 20.f))
        .HAlign(HAlign_Center)
        [
            SNew(SBox)
            .WidthOverride(840.f)
            [
                SNew(SVerticalBox)
                + SVerticalBox::Slot()
                .AutoHeight()
                .Padding(0.f, 0.f, 0.f, 8.f)
                [
                    SNew(STextBlock)
                    .Text(FText::FromString(TEXT("ANANTA  /  CITY")))
                    .Font(FCoreStyle::GetDefaultFontStyle("Bold", 12))
                    .ColorAndOpacity(FLinearColor(0.2f, 0.9f, 0.8f))
                ]
                + SVerticalBox::Slot()
                .AutoHeight()
                [
                    SNew(STextBlock)
                    .Text_Lambda([this]() { return L(TEXT("Cài đặt"), TEXT("Settings")); })
                    .Font(FCoreStyle::GetDefaultFontStyle("Bold", 28))
                    .ColorAndOpacity(FLinearColor::White)
                ]
                + SVerticalBox::Slot()
                .AutoHeight()
                .Padding(0.f, 6.f, 0.f, 14.f)
                [
                    SNew(STextBlock)
                    .Text_Lambda([this]()
                    {
                        return L(TEXT("Đồ họa, hiển thị và ngôn ngữ. Thay đổi chỉ có hiệu lực khi Áp dụng."),
                            TEXT("Graphics, display and language. Changes take effect when you select Apply."));
                    })
                    .Font(FCoreStyle::GetDefaultFontStyle("Regular", 12))
                    .ColorAndOpacity(FLinearColor(0.67f, 0.77f, 0.85f))
                    .AutoWrapText(true)
                ]
                + SVerticalBox::Slot()
                .FillHeight(1.f)
                [
                    SNew(SScrollBox)
                    .ScrollBarAlwaysVisible(true)
                    .ScrollWhenFocusChanges(EScrollWhenFocusChanges::InstantScroll)
                    .NavigationScrollPadding(8.f)
                    + SScrollBox::Slot()
                    .Padding(0.f, 0.f, 12.f, 8.f)
                    [Rows]
                ]
                + SVerticalBox::Slot()
                .AutoHeight()
                .Padding(0.f, 12.f, 0.f, 0.f)
                [BuildFooter()]
            ]
        ];
}

TSharedRef<SWidget> SCitySettingsPanel::BuildFooter()
{
    return SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(0.f, 0.f, 0.f, 10.f)
        [
            SNew(STextBlock)
            .Text_Lambda([this]()
            {
                return bHasEdits
                    ? L(TEXT("Có thay đổi chưa áp dụng"), TEXT("You have unapplied changes"))
                    : L(TEXT("Đang dùng cài đặt đã lưu"), TEXT("Using saved settings"));
            })
            .Font(FCoreStyle::GetDefaultFontStyle("Regular", 12))
            .ColorAndOpacity(FLinearColor(0.2f, 0.9f, 0.8f))
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(SHorizontalBox)
            + SHorizontalBox::Slot()
            .AutoWidth()
            [
                SNew(SButton)
                .ContentPadding(FMargin(18.f, 10.f))
                .OnClicked(this, &SCitySettingsPanel::ResetDraft)
                [
                    SNew(STextBlock)
                    .Text_Lambda([this]() { return L(TEXT("Mặc định"), TEXT("Defaults")); })
                    .Font(FCoreStyle::GetDefaultFontStyle("Regular", 13))
                ]
            ]
            + SHorizontalBox::Slot()
            .FillWidth(1.f)
            .VAlign(VAlign_Center)
            .HAlign(HAlign_Center)
            [
                SNew(STextBlock)
                .Text_Lambda([this]()
                {
                    return L(TEXT("Tab: chọn  ·  Enter: xác nhận"), TEXT("Tab: navigate  ·  Enter: select"));
                })
                .Font(FCoreStyle::GetDefaultFontStyle("Regular", 10))
                .ColorAndOpacity(FLinearColor(0.67f, 0.77f, 0.85f))
            ]
            + SHorizontalBox::Slot()
            .AutoWidth()
            .Padding(0.f, 0.f, 10.f, 0.f)
            [
                SNew(SButton)
                .ContentPadding(FMargin(18.f, 10.f))
                .OnClicked(this, &SCitySettingsPanel::CloseDraft)
                [
                    SNew(STextBlock)
                    .Text_Lambda([this]() { return L(TEXT("Đóng / Hủy · Esc"), TEXT("Close / Cancel · Esc")); })
                    .Font(FCoreStyle::GetDefaultFontStyle("Regular", 13))
                ]
            ]
            + SHorizontalBox::Slot()
            .AutoWidth()
            [
                SNew(SButton)
                .ContentPadding(FMargin(24.f, 10.f))
                .ButtonColorAndOpacity(FLinearColor(0.05f, 0.6f, 0.5f))
                .OnClicked(this, &SCitySettingsPanel::ApplyClicked)
                [
                    SNew(STextBlock)
                    .Text_Lambda([this]() { return L(TEXT("Áp dụng"), TEXT("Apply")); })
                    .Font(FCoreStyle::GetDefaultFontStyle("Bold", 13))
                    .ColorAndOpacity(FLinearColor::White)
                ]
            ]
        ];
}

void SCitySettingsPanel::AddSection(const TSharedRef<SVerticalBox>& Rows,
    const TCHAR* Vietnamese, const TCHAR* English)
{
    Rows->AddSlot()
        .AutoHeight()
        .Padding(0.f, 14.f, 0.f, 8.f)
        [
            SNew(STextBlock)
            .Text_Lambda([this, Vietnamese, English]() { return L(Vietnamese, English); })
            .Font(FCoreStyle::GetDefaultFontStyle("Bold", 15))
            .ColorAndOpacity(FLinearColor(0.2f, 0.9f, 0.8f))
        ];
}

void SCitySettingsPanel::AddRow(const TSharedRef<SVerticalBox>& Rows,
    const TCHAR* Vietnamese, const TCHAR* English, const TSharedRef<SWidget>& Control)
{
    Rows->AddSlot()
        .AutoHeight()
        .Padding(0.f, 2.f)
        [
            SNew(SBorder)
            .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
            .BorderBackgroundColor(FLinearColor(0.025f, 0.047f, 0.075f))
            .Padding(FMargin(14.f, 7.f))
            [
                SNew(SHorizontalBox)
                + SHorizontalBox::Slot()
                .FillWidth(1.f)
                .VAlign(VAlign_Center)
                .Padding(0.f, 0.f, 16.f, 0.f)
                [
                    SNew(STextBlock)
                    .Text_Lambda([this, Vietnamese, English]() { return L(Vietnamese, English); })
                    .Font(FCoreStyle::GetDefaultFontStyle("Regular", 13))
                    .ColorAndOpacity(FLinearColor(0.9f, 0.95f, 1.f))
                    .AutoWrapText(true)
                ]
                + SHorizontalBox::Slot()
                .AutoWidth()
                .VAlign(VAlign_Center)
                [
                    SNew(SBox)
                    .WidthOverride(245.f)
                    [Control]
                ]
            ]
        ];
}
