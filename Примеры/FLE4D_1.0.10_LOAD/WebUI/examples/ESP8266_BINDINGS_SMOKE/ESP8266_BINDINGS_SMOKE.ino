#include <FLProgWebUi.h>
#include <adapters/FLProgWebUiFlprogNetworkPagedHttp.h>

static const FLProgWebUiChannelDescriptor channels[] = {
    {"temperature", FLPROG_WEBUI_FLOAT, FLPROG_WEBUI_PUBLISH, 101},
    {"setpoint", FLPROG_WEBUI_FLOAT, FLPROG_WEBUI_DUPLEX, 102},
    {"alarm", FLPROG_WEBUI_BOOL, FLPROG_WEBUI_PUBLISH, 103},
    {"temperature_2", FLPROG_WEBUI_FLOAT, FLPROG_WEBUI_PUBLISH, 104},
};
static FLProgWebUiChannelSlot slots[sizeof(channels) / sizeof(channels[0])];
static FLProgWebUiModel model(channels, slots, sizeof(channels) / sizeof(channels[0]));
static const FLProgWebUiBindingDescriptor sliderBindings[] = {
    {"setpoint", "setpoint", "duplex"},
    {"alarm", "alarm", "publish"},
};
static const FLProgWebUiBindingDescriptor chartBindings[] = {
    {"series1", "temperature_2", "publish"},
};
static const FLProgWebUiWidgetDescriptor widgets[] = {
    {"temperature-slider", "slider", "Temperature", "temperature", "", "#22d3ee", "normal",
     0, 100, 1, 1, 1, 6, 2, "main", "", "", sliderBindings, 2},
    {"temperature-chart", "chart", "Trend", "temperature", "", "#22d3ee", "normal",
     0, 100, 1, 1, 3, 12, 4, "main", "", "", chartBindings, 1},
};
static const FLProgWebUiPageDescriptor pages[] = {{"main", "Main"}};
static const FLProgWebUiThemeDescriptor theme = {"#0b1120", "#162237", "#ffffff", "#7367ff"};
static FLProgWebUiFlprogNetworkPagedHttp webUi(
    model, widgets, sizeof(widgets) / sizeof(widgets[0]), pages, 1, theme);

void setup() {}
void loop() {}
