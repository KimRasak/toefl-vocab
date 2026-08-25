// 词条 -> 单词真人发音音频映射（剑桥词典真人美音；例句走页面 TTS 朗读当前文本）
const AUDIO_MAP = {
 "nose": {
  "w": "00-w-nose.mp3",
  "s": null
 },
 "nasal": {
  "w": "01-w-nasal.mp3",
  "s": null
 },
 "nasal sacs": {
  "w": "02-w-nasal-sacs.mp3",
  "s": null
 },
 "mouth": {
  "w": "03-w-mouth.mp3",
  "s": null
 },
 "oral": {
  "w": "04-w-oral.mp3",
  "s": null
 },
 "ear": {
  "w": "05-w-ear.mp3",
  "s": null
 },
 "aural": {
  "w": "06-w-aural.mp3",
  "s": null
 },
 "otic": {
  "w": null,
  "s": null
 },
 "tooth": {
  "w": "08-w-tooth.mp3",
  "s": null
 },
 "dental": {
  "w": "09-w-dental.mp3",
  "s": null
 },
 "heart": {
  "w": "10-w-heart.mp3",
  "s": null
 },
 "cardiac": {
  "w": "11-w-cardiac.mp3",
  "s": null
 },
 "lung": {
  "w": "12-w-lung.mp3",
  "s": null
 },
 "pulmonary": {
  "w": "13-w-pulmonary.mp3",
  "s": null
 },
 "liver": {
  "w": "14-w-liver.mp3",
  "s": null
 },
 "hepatic": {
  "w": "15-w-hepatic.mp3",
  "s": null
 },
 "Pacific Ocean": {
  "w": "16-w-pacific-ocean.mp3",
  "s": null
 },
 "Atlantic Ocean": {
  "w": "17-w-atlantic-ocean.mp3",
  "s": null
 },
 "Indian Ocean": {
  "w": "18-w-indian-ocean.mp3",
  "s": null
 },
 "Arctic Ocean": {
  "w": "19-w-arctic-ocean.mp3",
  "s": null
 },
 "Southern Ocean": {
  "w": "20-w-southern-ocean.mp3",
  "s": null
 },
 "Mediterranean Sea": {
  "w": "21-w-mediterranean-sea.mp3",
  "s": null
 },
 "Red Sea": {
  "w": "22-w-red-sea.mp3",
  "s": null
 },
 "Black Sea": {
  "w": "23-w-black-sea.mp3",
  "s": null
 },
 "Caspian Sea": {
  "w": "24-w-caspian-sea.mp3",
  "s": null
 },
 "Baltic Sea": {
  "w": "25-w-baltic-sea.mp3",
  "s": null
 },
 "North Sea": {
  "w": "26-w-north-sea.mp3",
  "s": null
 },
 "Caribbean Sea": {
  "w": "27-w-caribbean-sea.mp3",
  "s": null
 },
 "Arabian Sea": {
  "w": "28-w-arabian-sea.mp3",
  "s": null
 },
 "South China Sea": {
  "w": "29-w-south-china-sea.mp3",
  "s": null
 },
 "Strait of Gibraltar": {
  "w": "30-w-strait-of-gibraltar.mp3",
  "s": null
 },
 "Strait of Malacca": {
  "w": "31-w-strait-of-malacca.mp3",
  "s": null
 },
 "English Channel": {
  "w": "32-w-english-channel.mp3",
  "s": null
 },
 "Bering Strait": {
  "w": "33-w-bering-strait.mp3",
  "s": null
 },
 "Strait of Hormuz": {
  "w": "34-w-strait-of-hormuz.mp3",
  "s": null
 },
 "Gulf of Mexico": {
  "w": "35-w-gulf-of-mexico.mp3",
  "s": null
 },
 "Persian Gulf": {
  "w": "36-w-persian-gulf.mp3",
  "s": null
 },
 "Gulf of Guinea": {
  "w": "37-w-gulf-of-guinea.mp3",
  "s": null
 },
 "Gulf of Alaska": {
  "w": "38-w-gulf-of-alaska.mp3",
  "s": null
 },
 "Bay of Bengal": {
  "w": "39-w-bay-of-bengal.mp3",
  "s": null
 },
 "Antarctica": {
  "w": "40-w-antarctica.mp3",
  "s": null
 },
 "Oceania": {
  "w": "41-w-oceania.mp3",
  "s": null
 },
 "microscopic marine plants": {
  "w": "42-w-microscopic-marine-plants.mp3",
  "s": null
 },
 "microorganisms": {
  "w": "43-w-microorganisms.mp3",
  "s": null
 },
 "chronological order": {
  "w": "44-w-chronological-order.mp3",
  "s": null
 },
 "flashback": {
  "w": "45-w-flashback.mp3",
  "s": null
 },
 "in medias res": {
  "w": "46-w-in-medias-res.mp3",
  "s": null
 },
 "non-linear": {
  "w": "47-w-non-linear.mp3",
  "s": null
 },
 "Ordovician-Silurian extinction": {
  "w": "48-w-ordovician-silurian-extinction.mp3",
  "s": null
 },
 "Late Devonian extinction": {
  "w": "49-w-late-devonian-extinction.mp3",
  "s": null
 },
 "Permian-Triassic extinction": {
  "w": "50-w-permian-triassic-extinction.mp3",
  "s": null
 },
 "The Great Dying": {
  "w": null,
  "s": null
 },
 "Triassic-Jurassic extinction": {
  "w": "52-w-triassic-jurassic-extinction.mp3",
  "s": null
 },
 "Cretaceous-Paleogene extinction": {
  "w": "53-w-cretaceous-paleogene-extinction.mp3",
  "s": null
 },
 "Ordovician": {
  "w": "54-w-ordovician.mp3",
  "s": null
 },
 "Devonian": {
  "w": "55-w-devonian.mp3",
  "s": null
 },
 "Permian": {
  "w": "56-w-permian.mp3",
  "s": null
 },
 "Triassic": {
  "w": "57-w-triassic.mp3",
  "s": null
 },
 "Cretaceous": {
  "w": "58-w-cretaceous.mp3",
  "s": null
 },
 "morning light": {
  "w": "59-w-morning-light.mp3",
  "s": null
 },
 "cairn": {
  "w": "60-w-cairn.mp3",
  "s": null
 },
 "ridge": {
  "w": "61-w-ridge.mp3",
  "s": null
 },
 "shrub": {
  "w": "62-w-shrub.mp3",
  "s": null
 },
 "hind feet": {
  "w": "63-w-hind-feet.mp3",
  "s": null
 },
 "forelimb": {
  "w": null,
  "s": null
 },
 "hind limb": {
  "w": "65-w-hind-limb.mp3",
  "s": null
 },
 "pectoral fin": {
  "w": "66-w-pectoral-fin.mp3",
  "s": null
 },
 "pelvic fin": {
  "w": "67-w-pelvic-fin.mp3",
  "s": null
 },
 "mandible": {
  "w": "68-w-mandible.mp3",
  "s": null
 },
 "maxilla": {
  "w": "69-w-maxilla.mp3",
  "s": null
 },
 "appendage": {
  "w": "70-w-appendage.mp3",
  "s": null
 },
 "cranium": {
  "w": "71-w-cranium.mp3",
  "s": null
 },
 "pectoral": {
  "w": "72-w-pectoral.mp3",
  "s": null
 },
 "pedal": {
  "w": "73-w-pedal.mp3",
  "s": null
 },
 "grasp": {
  "w": "74-w-grasp.mp3",
  "s": null
 },
 "manipulate": {
  "w": "75-w-manipulate.mp3",
  "s": null
 },
 "bite force": {
  "w": "76-w-bite-force.mp3",
  "s": null
 },
 "mastication": {
  "w": "77-w-mastication.mp3",
  "s": null
 },
 "prehensile": {
  "w": "78-w-prehensile.mp3",
  "s": null
 },
 "locomotion": {
  "w": "79-w-locomotion.mp3",
  "s": null
 },
 "anterior": {
  "w": "80-w-anterior.mp3",
  "s": null
 },
 "posterior": {
  "w": "81-w-posterior.mp3",
  "s": null
 },
 "ventral": {
  "w": "82-w-ventral.mp3",
  "s": null
 },
 "dorsal": {
  "w": "83-w-dorsal.mp3",
  "s": null
 },
 "proximal": {
  "w": "84-w-proximal.mp3",
  "s": null
 },
 "distal": {
  "w": "85-w-distal.mp3",
  "s": null
 },
 "Alabama": {
  "w": "86-w-alabama.mp3",
  "s": null
 },
 "State of Alabama": {
  "w": "87-w-state-of-alabama.mp3",
  "s": null
 },
 "Alaska": {
  "w": "88-w-alaska.mp3",
  "s": null
 },
 "State of Alaska": {
  "w": "89-w-state-of-alaska.mp3",
  "s": null
 },
 "Arizona": {
  "w": "90-w-arizona.mp3",
  "s": null
 },
 "State of Arizona": {
  "w": "91-w-state-of-arizona.mp3",
  "s": null
 },
 "Arkansas": {
  "w": "92-w-arkansas.mp3",
  "s": null
 },
 "State of Arkansas": {
  "w": "93-w-state-of-arkansas.mp3",
  "s": null
 },
 "California": {
  "w": "94-w-california.mp3",
  "s": null
 },
 "State of California": {
  "w": "95-w-state-of-california.mp3",
  "s": null
 },
 "Colorado": {
  "w": "96-w-colorado.mp3",
  "s": null
 },
 "State of Colorado": {
  "w": "97-w-state-of-colorado.mp3",
  "s": null
 },
 "Connecticut": {
  "w": "98-w-connecticut.mp3",
  "s": null
 },
 "State of Connecticut": {
  "w": "99-w-state-of-connecticut.mp3",
  "s": null
 },
 "Delaware": {
  "w": "100-w-delaware.mp3",
  "s": null
 },
 "State of Delaware": {
  "w": "101-w-state-of-delaware.mp3",
  "s": null
 },
 "Florida": {
  "w": "102-w-florida.mp3",
  "s": null
 },
 "State of Florida": {
  "w": "103-w-state-of-florida.mp3",
  "s": null
 },
 "Georgia": {
  "w": "104-w-georgia.mp3",
  "s": null
 },
 "State of Georgia": {
  "w": "105-w-state-of-georgia.mp3",
  "s": null
 },
 "Hawaii": {
  "w": "106-w-hawaii.mp3",
  "s": null
 },
 "State of Hawaii": {
  "w": "107-w-state-of-hawaii.mp3",
  "s": null
 },
 "Idaho": {
  "w": "108-w-idaho.mp3",
  "s": null
 },
 "State of Idaho": {
  "w": "109-w-state-of-idaho.mp3",
  "s": null
 },
 "Illinois": {
  "w": "110-w-illinois.mp3",
  "s": null
 },
 "State of Illinois": {
  "w": "111-w-state-of-illinois.mp3",
  "s": null
 },
 "Indiana": {
  "w": "112-w-indiana.mp3",
  "s": null
 },
 "State of Indiana": {
  "w": "113-w-state-of-indiana.mp3",
  "s": null
 },
 "Iowa": {
  "w": "114-w-iowa.mp3",
  "s": null
 },
 "State of Iowa": {
  "w": "115-w-state-of-iowa.mp3",
  "s": null
 },
 "Kansas": {
  "w": "116-w-kansas.mp3",
  "s": null
 },
 "State of Kansas": {
  "w": "117-w-state-of-kansas.mp3",
  "s": null
 },
 "Kentucky": {
  "w": "118-w-kentucky.mp3",
  "s": null
 },
 "State of Kentucky": {
  "w": "119-w-state-of-kentucky.mp3",
  "s": null
 },
 "Louisiana": {
  "w": "120-w-louisiana.mp3",
  "s": null
 },
 "State of Louisiana": {
  "w": "121-w-state-of-louisiana.mp3",
  "s": null
 },
 "Maine": {
  "w": "122-w-maine.mp3",
  "s": null
 },
 "State of Maine": {
  "w": "123-w-state-of-maine.mp3",
  "s": null
 },
 "Maryland": {
  "w": "124-w-maryland.mp3",
  "s": null
 },
 "State of Maryland": {
  "w": "125-w-state-of-maryland.mp3",
  "s": null
 },
 "Massachusetts": {
  "w": "126-w-massachusetts.mp3",
  "s": null
 },
 "State of Massachusetts": {
  "w": "127-w-state-of-massachusetts.mp3",
  "s": null
 },
 "Michigan": {
  "w": "128-w-michigan.mp3",
  "s": null
 },
 "State of Michigan": {
  "w": "129-w-state-of-michigan.mp3",
  "s": null
 },
 "Minnesota": {
  "w": "130-w-minnesota.mp3",
  "s": null
 },
 "State of Minnesota": {
  "w": "131-w-state-of-minnesota.mp3",
  "s": null
 },
 "Mississippi": {
  "w": "132-w-mississippi.mp3",
  "s": null
 },
 "State of Mississippi": {
  "w": "133-w-state-of-mississippi.mp3",
  "s": null
 },
 "Missouri": {
  "w": "134-w-missouri.mp3",
  "s": null
 },
 "State of Missouri": {
  "w": "135-w-state-of-missouri.mp3",
  "s": null
 },
 "Montana": {
  "w": "136-w-montana.mp3",
  "s": null
 },
 "State of Montana": {
  "w": "137-w-state-of-montana.mp3",
  "s": null
 },
 "Nebraska": {
  "w": "138-w-nebraska.mp3",
  "s": null
 },
 "State of Nebraska": {
  "w": "139-w-state-of-nebraska.mp3",
  "s": null
 },
 "Nevada": {
  "w": "140-w-nevada.mp3",
  "s": null
 },
 "State of Nevada": {
  "w": "141-w-state-of-nevada.mp3",
  "s": null
 },
 "New Hampshire": {
  "w": "142-w-new-hampshire.mp3",
  "s": null
 },
 "State of New Hampshire": {
  "w": "143-w-state-of-new-hampshire.mp3",
  "s": null
 },
 "New Jersey": {
  "w": "144-w-new-jersey.mp3",
  "s": null
 },
 "State of New Jersey": {
  "w": "145-w-state-of-new-jersey.mp3",
  "s": null
 },
 "New Mexico": {
  "w": "146-w-new-mexico.mp3",
  "s": null
 },
 "State of New Mexico": {
  "w": "147-w-state-of-new-mexico.mp3",
  "s": null
 },
 "New York": {
  "w": "148-w-new-york.mp3",
  "s": null
 },
 "State of New York": {
  "w": "149-w-state-of-new-york.mp3",
  "s": null
 },
 "North Carolina": {
  "w": "150-w-north-carolina.mp3",
  "s": null
 },
 "State of North Carolina": {
  "w": "151-w-state-of-north-carolina.mp3",
  "s": null
 },
 "North Dakota": {
  "w": "152-w-north-dakota.mp3",
  "s": null
 },
 "State of North Dakota": {
  "w": "153-w-state-of-north-dakota.mp3",
  "s": null
 },
 "Ohio": {
  "w": "154-w-ohio.mp3",
  "s": null
 },
 "State of Ohio": {
  "w": "155-w-state-of-ohio.mp3",
  "s": null
 },
 "Oklahoma": {
  "w": "156-w-oklahoma.mp3",
  "s": null
 },
 "State of Oklahoma": {
  "w": "157-w-state-of-oklahoma.mp3",
  "s": null
 },
 "Oregon": {
  "w": "158-w-oregon.mp3",
  "s": null
 },
 "State of Oregon": {
  "w": "159-w-state-of-oregon.mp3",
  "s": null
 },
 "Pennsylvania": {
  "w": "160-w-pennsylvania.mp3",
  "s": null
 },
 "State of Pennsylvania": {
  "w": "161-w-state-of-pennsylvania.mp3",
  "s": null
 },
 "Rhode Island": {
  "w": "162-w-rhode-island.mp3",
  "s": null
 },
 "State of Rhode Island": {
  "w": "163-w-state-of-rhode-island.mp3",
  "s": null
 },
 "South Carolina": {
  "w": "164-w-south-carolina.mp3",
  "s": null
 },
 "State of South Carolina": {
  "w": "165-w-state-of-south-carolina.mp3",
  "s": null
 },
 "South Dakota": {
  "w": "166-w-south-dakota.mp3",
  "s": null
 },
 "State of South Dakota": {
  "w": "167-w-state-of-south-dakota.mp3",
  "s": null
 },
 "Tennessee": {
  "w": "168-w-tennessee.mp3",
  "s": null
 },
 "State of Tennessee": {
  "w": "169-w-state-of-tennessee.mp3",
  "s": null
 },
 "Texas": {
  "w": "170-w-texas.mp3",
  "s": null
 },
 "State of Texas": {
  "w": "171-w-state-of-texas.mp3",
  "s": null
 },
 "Utah": {
  "w": "172-w-utah.mp3",
  "s": null
 },
 "State of Utah": {
  "w": "173-w-state-of-utah.mp3",
  "s": null
 },
 "Vermont": {
  "w": "174-w-vermont.mp3",
  "s": null
 },
 "State of Vermont": {
  "w": "175-w-state-of-vermont.mp3",
  "s": null
 },
 "Virginia": {
  "w": "176-w-virginia.mp3",
  "s": null
 },
 "State of Virginia": {
  "w": "177-w-state-of-virginia.mp3",
  "s": null
 },
 "Washington": {
  "w": "178-w-washington.mp3",
  "s": null
 },
 "State of Washington": {
  "w": "179-w-state-of-washington.mp3",
  "s": null
 },
 "West Virginia": {
  "w": "180-w-west-virginia.mp3",
  "s": null
 },
 "State of West Virginia": {
  "w": "181-w-state-of-west-virginia.mp3",
  "s": null
 },
 "Wisconsin": {
  "w": "182-w-wisconsin.mp3",
  "s": null
 },
 "State of Wisconsin": {
  "w": "183-w-state-of-wisconsin.mp3",
  "s": null
 },
 "Wyoming": {
  "w": "184-w-wyoming.mp3",
  "s": null
 },
 "State of Wyoming": {
  "w": "185-w-state-of-wyoming.mp3",
  "s": null
 },
 "the Renaissance": {
  "w": "186-w-the-renaissance.mp3",
  "s": null
 },
 "Humanism": {
  "w": "187-w-humanism.mp3",
  "s": null
 },
 "the Reformation": {
  "w": "188-w-the-reformation.mp3",
  "s": null
 },
 "Protestantism": {
  "w": "189-w-protestantism.mp3",
  "s": null
 },
 "Martin Luther": {
  "w": "190-w-martin-luther.mp3",
  "s": null
 },
 "the Scientific Revolution": {
  "w": null,
  "s": null
 },
 "Scientific Method": {
  "w": "192-w-scientific-method.mp3",
  "s": null
 },
 "Copernicus": {
  "w": null,
  "s": null
 },
 "Galileo": {
  "w": null,
  "s": null
 },
 "Newton": {
  "w": "195-w-newton.mp3",
  "s": null
 },
 "Realism": {
  "w": "196-w-realism.mp3",
  "s": null
 },
 "Impressionism": {
  "w": "197-w-impressionism.mp3",
  "s": null
 },
 "Modernism": {
  "w": "198-w-modernism.mp3",
  "s": null
 },
 "methane": {
  "w": "199-w-methane.mp3",
  "s": null
 },
 "natural gas": {
  "w": "200-w-natural-gas.mp3",
  "s": null
 },
 "greenhouse gas": {
  "w": "201-w-greenhouse-gas.mp3",
  "s": null
 },
 "greenhouse effect": {
  "w": "202-w-greenhouse-effect.mp3",
  "s": null
 },
 "global warming": {
  "w": "203-w-global-warming.mp3",
  "s": null
 },
 "climate change": {
  "w": "204-w-climate-change.mp3",
  "s": null
 },
 "carbon dioxide": {
  "w": "205-w-carbon-dioxide.mp3",
  "s": null
 },
 "carbon monoxide": {
  "w": "206-w-carbon-monoxide.mp3",
  "s": null
 },
 "fossil fuel": {
  "w": "207-w-fossil-fuel.mp3",
  "s": null
 },
 "hydrocarbon": {
  "w": "208-w-hydrocarbon.mp3",
  "s": null
 },
 "permafrost": {
  "w": "209-w-permafrost.mp3",
  "s": null
 },
 "wetland": {
  "w": "210-w-wetland.mp3",
  "s": null
 },
 "livestock": {
  "w": "211-w-livestock.mp3",
  "s": null
 },
 "anaerobic": {
  "w": "212-w-anaerobic.mp3",
  "s": null
 },
 "microorganism": {
  "w": "213-w-microorganism.mp3",
  "s": null
 },
 "carbon cycle": {
  "w": "214-w-carbon-cycle.mp3",
  "s": null
 },
 "carbon footprint": {
  "w": "215-w-carbon-footprint.mp3",
  "s": null
 },
 "carbon sequestration": {
  "w": "216-w-carbon-sequestration.mp3",
  "s": null
 },
 "feedback loop": {
  "w": "217-w-feedback-loop.mp3",
  "s": null
 },
 "methane hydrate": {
  "w": null,
  "s": null
 },
 "biogas": {
  "w": "219-w-biogas.mp3",
  "s": null
 },
 "combustion": {
  "w": "220-w-combustion.mp3",
  "s": null
 },
 "emission": {
  "w": "221-w-emission.mp3",
  "s": null
 },
 "atmosphere": {
  "w": "222-w-atmosphere.mp3",
  "s": null
 },
 "ozone": {
  "w": "223-w-ozone.mp3",
  "s": null
 },
 "ultraviolet radiation": {
  "w": null,
  "s": null
 },
 "hydraulic fracturing": {
  "w": "225-w-hydraulic-fracturing.mp3",
  "s": null
 },
 "shale gas": {
  "w": "226-w-shale-gas.mp3",
  "s": null
 },
 "renewable energy": {
  "w": "227-w-renewable-energy.mp3",
  "s": null
 },
 "solar panel": {
  "w": "228-w-solar-panel.mp3",
  "s": null
 },
 "wind turbine": {
  "w": "229-w-wind-turbine.mp3",
  "s": null
 },
 "geothermal energy": {
  "w": null,
  "s": null
 },
 "nuclear power": {
  "w": "231-w-nuclear-power.mp3",
  "s": null
 },
 "sediment": {
  "w": "232-w-sediment.mp3",
  "s": null
 },
 "peat": {
  "w": "233-w-peat.mp3",
  "s": null
 },
 "decompose": {
  "w": "234-w-decompose.mp3",
  "s": null
 },
 "smog": {
  "w": "235-w-smog.mp3",
  "s": null
 },
 "acid rain": {
  "w": "236-w-acid-rain.mp3",
  "s": null
 },
 "sustainable": {
  "w": "237-w-sustainable.mp3",
  "s": null
 },
 "recycle": {
  "w": "238-w-recycle.mp3",
  "s": null
 },
 "transverse flute": {
  "w": "239-w-transverse-flute.mp3",
  "s": null
 },
 "flute": {
  "w": "240-w-flute.mp3",
  "s": null
 },
 "piccolo": {
  "w": "241-w-piccolo.mp3",
  "s": null
 },
 "recorder": {
  "w": "242-w-recorder.mp3",
  "s": null
 },
 "clarinet": {
  "w": "243-w-clarinet.mp3",
  "s": null
 },
 "oboe": {
  "w": "244-w-oboe.mp3",
  "s": null
 },
 "bassoon": {
  "w": "245-w-bassoon.mp3",
  "s": null
 },
 "saxophone": {
  "w": "246-w-saxophone.mp3",
  "s": null
 },
 "English horn": {
  "w": "247-w-english-horn.mp3",
  "s": null
 },
 "trumpet": {
  "w": "248-w-trumpet.mp3",
  "s": null
 },
 "cornet": {
  "w": "249-w-cornet.mp3",
  "s": null
 },
 "French horn": {
  "w": "250-w-french-horn.mp3",
  "s": null
 },
 "trombone": {
  "w": "251-w-trombone.mp3",
  "s": null
 },
 "tuba": {
  "w": "252-w-tuba.mp3",
  "s": null
 },
 "violin": {
  "w": "253-w-violin.mp3",
  "s": null
 },
 "viola": {
  "w": "254-w-viola.mp3",
  "s": null
 },
 "cello": {
  "w": "255-w-cello.mp3",
  "s": null
 },
 "double bass": {
  "w": "256-w-double-bass.mp3",
  "s": null
 },
 "harp": {
  "w": "257-w-harp.mp3",
  "s": null
 },
 "guitar": {
  "w": "258-w-guitar.mp3",
  "s": null
 },
 "lute": {
  "w": "259-w-lute.mp3",
  "s": null
 },
 "banjo": {
  "w": "260-w-banjo.mp3",
  "s": null
 },
 "mandolin": {
  "w": "261-w-mandolin.mp3",
  "s": null
 },
 "drum": {
  "w": "262-w-drum.mp3",
  "s": null
 },
 "snare drum": {
  "w": "263-w-snare-drum.mp3",
  "s": null
 },
 "bass drum": {
  "w": "264-w-bass-drum.mp3",
  "s": null
 },
 "timpani": {
  "w": "265-w-timpani.mp3",
  "s": null
 },
 "cymbal": {
  "w": "266-w-cymbal.mp3",
  "s": null
 },
 "triangle": {
  "w": "267-w-triangle.mp3",
  "s": null
 },
 "tambourine": {
  "w": "268-w-tambourine.mp3",
  "s": null
 },
 "xylophone": {
  "w": "269-w-xylophone.mp3",
  "s": null
 },
 "marimba": {
  "w": "270-w-marimba.mp3",
  "s": null
 },
 "glockenspiel": {
  "w": "271-w-glockenspiel.mp3",
  "s": null
 },
 "piano": {
  "w": "272-w-piano.mp3",
  "s": null
 },
 "organ": {
  "w": "273-w-organ.mp3",
  "s": null
 },
 "harpsichord": {
  "w": "274-w-harpsichord.mp3",
  "s": null
 },
 "accordion": {
  "w": "275-w-accordion.mp3",
  "s": null
 },
 "synthesizer": {
  "w": "276-w-synthesizer.mp3",
  "s": null
 },
 "bagpipe": {
  "w": "277-w-bagpipe.mp3",
  "s": null
 },
 "sitar": {
  "w": "278-w-sitar.mp3",
  "s": null
 },
 "pan flute": {
  "w": null,
  "s": null
 },
 "harmonica": {
  "w": "280-w-harmonica.mp3",
  "s": null
 },
 "didgeridoo": {
  "w": "281-w-didgeridoo.mp3",
  "s": null
 },
 "felt": {
  "w": "282-w-felt.mp3",
  "s": null
 },
 "hands": {
  "w": "283-w-hands.mp3",
  "s": null
 },
 "pupil": {
  "w": "284-w-pupil.mp3",
  "s": null
 },
 "iris": {
  "w": "285-w-iris.mp3",
  "s": null
 },
 "palm": {
  "w": "286-w-palm.mp3",
  "s": null
 },
 "trunk": {
  "w": "287-w-trunk.mp3",
  "s": null
 },
 "head": {
  "w": "288-w-head.mp3",
  "s": null
 },
 "foot": {
  "w": "289-w-foot.mp3",
  "s": null
 },
 "arm": {
  "w": "290-w-arm.mp3",
  "s": null
 },
 "bat": {
  "w": "291-w-bat.mp3",
  "s": null
 },
 "crane": {
  "w": "292-w-crane.mp3",
  "s": null
 },
 "seal": {
  "w": "293-w-seal.mp3",
  "s": null
 },
 "bear": {
  "w": "294-w-bear.mp3",
  "s": null
 },
 "swallow": {
  "w": "295-w-swallow.mp3",
  "s": null
 },
 "mole": {
  "w": "296-w-mole.mp3",
  "s": null
 },
 "current": {
  "w": "297-w-current.mp3",
  "s": null
 },
 "conductor": {
  "w": "298-w-conductor.mp3",
  "s": null
 },
 "pitch": {
  "w": "299-w-pitch.mp3",
  "s": null
 },
 "work": {
  "w": "300-w-work.mp3",
  "s": null
 },
 "mass": {
  "w": "301-w-mass.mp3",
  "s": null
 },
 "solution": {
  "w": "302-w-solution.mp3",
  "s": null
 },
 "cell": {
  "w": "303-w-cell.mp3",
  "s": null
 },
 "plate": {
  "w": "304-w-plate.mp3",
  "s": null
 },
 "fault": {
  "w": "305-w-fault.mp3",
  "s": null
 },
 "crust": {
  "w": "306-w-crust.mp3",
  "s": null
 },
 "mantle": {
  "w": "307-w-mantle.mp3",
  "s": null
 },
 "core": {
  "w": "308-w-core.mp3",
  "s": null
 },
 "fold": {
  "w": "309-w-fold.mp3",
  "s": null
 },
 "note": {
  "w": "310-w-note.mp3",
  "s": null
 },
 "rest": {
  "w": "311-w-rest.mp3",
  "s": null
 },
 "staff": {
  "w": "312-w-staff.mp3",
  "s": null
 },
 "bridge": {
  "w": "313-w-bridge.mp3",
  "s": null
 },
 "bow": {
  "w": "314-w-bow.mp3",
  "s": null
 },
 "scale": {
  "w": "315-w-scale.mp3",
  "s": null
 },
 "key": {
  "w": "316-w-key.mp3",
  "s": null
 },
 "novel": {
  "w": "317-w-novel.mp3",
  "s": null
 },
 "plot": {
  "w": "318-w-plot.mp3",
  "s": null
 },
 "table": {
  "w": "319-w-table.mp3",
  "s": null
 },
 "figure": {
  "w": "320-w-figure.mp3",
  "s": null
 },
 "mean": {
  "w": "321-w-mean.mp3",
  "s": null
 },
 "function": {
  "w": "322-w-function.mp3",
  "s": null
 },
 "interest": {
  "w": "323-w-interest.mp3",
  "s": null
 },
 "capital": {
  "w": "324-w-capital.mp3",
  "s": null
 },
 "stock": {
  "w": "325-w-stock.mp3",
  "s": null
 },
 "compound": {
  "w": "326-w-compound.mp3",
  "s": null
 },
 "revolution": {
  "w": "327-w-revolution.mp3",
  "s": null
 },
 "deposit": {
  "w": "338-w-deposit.mp3",
  "s": null
 },
 "trace": {
  "w": "329-w-trace.mp3",
  "s": null
 },
 "press": {
  "w": "330-w-press.mp3",
  "s": null
 },
 "revise": {
  "w": "331-w-revise.mp3",
  "s": null
 },
 "address": {
  "w": "332-w-address.mp3",
  "s": null
 },
 "season": {
  "w": "333-w-season.mp3",
  "s": null
 },
 "limestone": {
  "w": "334-w-limestone.mp3",
  "s": null
 },
 "sulfuric acid": {
  "w": "335-w-sulfuric-acid.mp3",
  "s": null
 },
 "dissolve": {
  "w": "336-w-dissolve.mp3",
  "s": null
 },
 "dissolution": {
  "w": "337-w-dissolution.mp3",
  "s": null
 },
 "precipitation": {
  "w": "339-w-precipitation.mp3",
  "s": null
 },
 "gypsum": {
  "w": "340-w-gypsum.mp3",
  "s": null
 },
 "anhydrite": {
  "w": "341-w-anhydrite.mp3",
  "s": null
 },
 "carbonate": {
  "w": "342-w-carbonate.mp3",
  "s": null
 },
 "calcite": {
  "w": null,
  "s": null
 },
 "acidic": {
  "w": "344-w-acidic.mp3",
  "s": null
 },
 "erosion": {
  "w": "345-w-erosion.mp3",
  "s": null
 },
 "groundwater": {
  "w": "346-w-groundwater.mp3",
  "s": null
 },
 "cave": {
  "w": "347-w-cave.mp3",
  "s": null
 },
 "cavern": {
  "w": "348-w-cavern.mp3",
  "s": null
 },
 "formation": {
  "w": "349-w-formation.mp3",
  "s": null
 },
 "speleothem": {
  "w": null,
  "s": null
 },
 "stalactite": {
  "w": "351-w-stalactite.mp3",
  "s": null
 },
 "stalagmite": {
  "w": "352-w-stalagmite.mp3",
  "s": null
 },
 "permeable": {
  "w": "353-w-permeable.mp3",
  "s": null
 },
 "fracture": {
  "w": "354-w-fracture.mp3",
  "s": null
 },
 "reaction": {
  "w": "355-w-reaction.mp3",
  "s": null
 },
 "by-product": {
  "w": "356-w-by-product.mp3",
  "s": null
 },
 "evidence": {
  "w": "357-w-evidence.mp3",
  "s": null
 },
 "instead of": {
  "w": "358-w-instead-of.mp3",
  "s": null
 },
 "rather than": {
  "w": null,
  "s": null
 },
 "Lechuguilla Cave": {
  "w": null,
  "s": null
 },
 "track meet": {
  "w": "361-w-track-meet.mp3",
  "s": null
 },
 "track": {
  "w": "362-w-track.mp3",
  "s": null
 },
 "varsity": {
  "w": "363-w-varsity.mp3",
  "s": null
 },
 "intramural": {
  "w": "364-w-intramural.mp3",
  "s": null
 },
 "tournament": {
  "w": "365-w-tournament.mp3",
  "s": null
 },
 "championship": {
  "w": "366-w-championship.mp3",
  "s": null
 },
 "coach": {
  "w": "367-w-coach.mp3",
  "s": null
 },
 "athlete": {
  "w": "368-w-athlete.mp3",
  "s": null
 },
 "captain": {
  "w": "369-w-captain.mp3",
  "s": null
 },
 "syllabus": {
  "w": "370-w-syllabus.mp3",
  "s": null
 },
 "prerequisite": {
  "w": "371-w-prerequisite.mp3",
  "s": null
 },
 "elective": {
  "w": "372-w-elective.mp3",
  "s": null
 },
 "credit": {
  "w": "373-w-credit.mp3",
  "s": null
 },
 "semester / term": {
  "w": "374-w-semester-term.mp3",
  "s": null
 },
 "major": {
  "w": "375-w-major.mp3",
  "s": null
 },
 "minor": {
  "w": "376-w-minor.mp3",
  "s": null
 },
 "advisor": {
  "w": null,
  "s": null
 },
 "office hours": {
  "w": "378-w-office-hours.mp3",
  "s": null
 },
 "registration": {
  "w": "379-w-registration.mp3",
  "s": null
 },
 "enroll": {
  "w": "380-w-enroll.mp3",
  "s": null
 },
 "transcript": {
  "w": "381-w-transcript.mp3",
  "s": null
 },
 "midterm": {
  "w": "382-w-midterm.mp3",
  "s": null
 },
 "deadline": {
  "w": "383-w-deadline.mp3",
  "s": null
 },
 "extension": {
  "w": "384-w-extension.mp3",
  "s": null
 },
 "term paper": {
  "w": "385-w-term-paper.mp3",
  "s": null
 },
 "thesis": {
  "w": "386-w-thesis.mp3",
  "s": null
 },
 "dissertation": {
  "w": "387-w-dissertation.mp3",
  "s": null
 },
 "seminar": {
  "w": "388-w-seminar.mp3",
  "s": null
 },
 "plagiarism": {
  "w": "389-w-plagiarism.mp3",
  "s": null
 },
 "citation": {
  "w": "390-w-citation.mp3",
  "s": null
 },
 "check out": {
  "w": "391-w-check-out.mp3",
  "s": null
 },
 "renew": {
  "w": "392-w-renew.mp3",
  "s": null
 },
 "overdue": {
  "w": "393-w-overdue.mp3",
  "s": null
 },
 "fine": {
  "w": "394-w-fine.mp3",
  "s": null
 },
 "reserve": {
  "w": "395-w-reserve.mp3",
  "s": null
 },
 "periodical": {
  "w": "396-w-periodical.mp3",
  "s": null
 },
 "journal": {
  "w": "397-w-journal.mp3",
  "s": null
 },
 "interlibrary loan": {
  "w": "398-w-interlibrary-loan.mp3",
  "s": null
 },
 "dormitory / dorm": {
  "w": "399-w-dormitory-dorm.mp3",
  "s": null
 },
 "roommate": {
  "w": "400-w-roommate.mp3",
  "s": null
 },
 "dining hall / cafeteria": {
  "w": "401-w-dining-hall-cafeteria.mp3",
  "s": null
 },
 "meal plan": {
  "w": null,
  "s": null
 },
 "orientation": {
  "w": "403-w-orientation.mp3",
  "s": null
 },
 "extracurricular": {
  "w": "404-w-extracurricular.mp3",
  "s": null
 },
 "tuition": {
  "w": "405-w-tuition.mp3",
  "s": null
 },
 "scholarship": {
  "w": "406-w-scholarship.mp3",
  "s": null
 },
 "financial aid": {
  "w": "407-w-financial-aid.mp3",
  "s": null
 },
 "grant": {
  "w": "408-w-grant.mp3",
  "s": null
 },
 "loan": {
  "w": "409-w-loan.mp3",
  "s": null
 },
 "internship": {
  "w": "410-w-internship.mp3",
  "s": null
 },
 "career fair": {
  "w": "411-w-career-fair.mp3",
  "s": null
 },
 "resume": {
  "w": "412-w-resume.mp3",
  "s": null
 },
 "lease": {
  "w": "413-w-lease.mp3",
  "s": null
 },
 "utilities": {
  "w": "414-w-utilities.mp3",
  "s": null
 },
 "off-campus": {
  "w": null,
  "s": null
 },
 "commuter": {
  "w": "416-w-commuter.mp3",
  "s": null
 },
 "shuttle bus": {
  "w": null,
  "s": null
 }
};
