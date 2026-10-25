struct BaselineClientContext {
        bool used;
        uint8_t state;
        uint8_t error;
        uint32_t startedAt;
        uint32_t lastActivityAt;
        uint32_t observedRxBytes;
        uint32_t observedTxBytes;

        char line[FLPROG_HTTP_SERVER_MAX_REQUEST_LINE + 1];
        uint16_t lineLength;
        uint32_t headerBytes;

        uint8_t method;
        char methodName[16];
        uint8_t httpMajor;
        uint8_t httpMinor;
        char uri[FLPROG_HTTP_SERVER_MAX_URI_LENGTH + 1];
        char host[FLPROG_HTTP_SERVER_MAX_HOST_LENGTH + 1];

        FLProgNetworkHttpServerPair headers[FLPROG_HTTP_SERVER_MAX_HEADERS];
        uint8_t headerCount;
        FLProgNetworkHttpServerArgument arguments[FLPROG_HTTP_SERVER_MAX_ARGUMENTS];
        uint8_t argumentCount;

        uint32_t contentLength;
        bool contentLengthSeen;
        uint32_t bodyReceived;
        char contentType[FLPROG_HTTP_SERVER_MAX_HEADER_VALUE_LENGTH + 1];
        uint8_t body[FLPROG_HTTP_SERVER_MAX_BODY_BYTES + 1];

        char response[FLPROG_HTTP_SERVER_MAX_RESPONSE_BYTES + 1];
        uint16_t responseLength;
        uint16_t responseOffset;
        bool responseOverflow;
        bool responseStructured;
};
static_assert(sizeof(BaselineClientContext)==FLProgNetworkHttpServer::clientContextBytes(), "HTTP context RAM grew");
