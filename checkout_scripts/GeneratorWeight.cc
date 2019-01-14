#include <memory>
#include <iostream>
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

class GeneratorWeight : public edm::one::EDAnalyzer<>  {
   public:
      explicit GeneratorWeight(const edm::ParameterSet&);
   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
      edm::EDGetTokenT<GenEventInfoProduct> MyGenEventInfoProduct_;
};


//
GeneratorWeight::GeneratorWeight(const edm::ParameterSet& iConfig){  
  //MyGenEventInfoProduct_ = consumes<GenEventInfoProduct>( iConfig.getParameter<edm::InputTag>("genSource") );
  MyGenEventInfoProduct_ = consumes<GenEventInfoProduct>( edm::InputTag("generator") );}

// ------------ method called for each event  ------------
void
GeneratorWeight::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup){
  edm::Handle<GenEventInfoProduct> GenEventInfo;
  iEvent.getByToken(MyGenEventInfoProduct_, GenEventInfo);
  std::cout << GenEventInfo->weight() << std::endl;}
DEFINE_FWK_MODULE(GeneratorWeight);
