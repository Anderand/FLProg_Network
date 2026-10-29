#pragma once
class FLProgNetworkInterface;
class FLProgNetworkService{bool bound=false;public:virtual ~FLProgNetworkService(){};bool attach(FLProgNetworkInterface&){bound=true;return true;}void detach(){bound=false;}bool isAttached()const{return bound;}virtual void pool()=0;};
