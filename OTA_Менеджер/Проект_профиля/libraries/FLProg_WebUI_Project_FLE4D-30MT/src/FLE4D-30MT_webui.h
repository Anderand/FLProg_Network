// Generated Web UI project entry: FLE4D-30MT
#pragma once
#ifdef FLPROG_WEBUI_SELECTED_PROJECT
#error "Web UI: only one project may be selected in a sketch"
#endif
#define FLPROG_WEBUI_SELECTED_PROJECT "FLE4D-30MT"
#include "FLE4D_30MT_descriptor.h"
#include <adapters/FLProgWebUiFlprogNetworkPagedHttp.h>
namespace flprog_webui_FLE4D_30MT {
inline bool begin(FLProgNetworkInterface &network) {
    if (!configure()) return false;
    static FLProgWebUiFlprogNetworkPagedHttp webUi(model, widgets, widgetCount, pages, pageCount, theme);
    webUi.setPolling(pollIntervalMs, pauseWhenHidden);
    return webUi.begin(network);
}
}
namespace flprog_webui_selected = flprog_webui_FLE4D_30MT;
// The interface macro is declared AFTER includes by FLProg. Expand it only
// at the call site, after the network instance and its macro exist.
#define FLPROG_WEBUI_BEGIN_SELECTED() flprog_webui_selected::begin(FLPROG_WIZNET_INTERFACE1)
