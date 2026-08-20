// 词条 -> 音频文件映射（自动生成）
const AUDIO_MAP = {
 "nose": {
  "w": "00-w-nose.mp3",
  "s": "00-s-nose.mp3"
 },
 "nasal": {
  "w": "01-w-nasal.mp3",
  "s": "01-s-nasal.mp3"
 },
 "nasal sacs": {
  "w": "02-w-nasal-sacs.mp3",
  "s": "02-s-nasal-sacs.mp3"
 },
 "mouth": {
  "w": "03-w-mouth.mp3",
  "s": "03-s-mouth.mp3"
 },
 "oral": {
  "w": "04-w-oral.mp3",
  "s": "04-s-oral.mp3"
 },
 "ear": {
  "w": "05-w-ear.mp3",
  "s": "05-s-ear.mp3"
 },
 "aural": {
  "w": "06-w-aural.mp3",
  "s": "06-s-aural.mp3"
 },
 "otic": {
  "w": "07-w-otic.mp3",
  "s": "07-s-otic.mp3"
 },
 "tooth": {
  "w": "08-w-tooth.mp3",
  "s": "08-s-tooth.mp3"
 },
 "dental": {
  "w": "09-w-dental.mp3",
  "s": "09-s-dental.mp3"
 },
 "heart": {
  "w": "10-w-heart.mp3",
  "s": "10-s-heart.mp3"
 },
 "cardiac": {
  "w": "11-w-cardiac.mp3",
  "s": "11-s-cardiac.mp3"
 },
 "lung": {
  "w": "12-w-lung.mp3",
  "s": "12-s-lung.mp3"
 },
 "pulmonary": {
  "w": "13-w-pulmonary.mp3",
  "s": "13-s-pulmonary.mp3"
 },
 "liver": {
  "w": "14-w-liver.mp3",
  "s": "14-s-liver.mp3"
 },
 "hepatic": {
  "w": "15-w-hepatic.mp3",
  "s": "15-s-hepatic.mp3"
 },
 "Pacific Ocean": {
  "w": "16-w-pacific-ocean.mp3",
  "s": "16-s-pacific-ocean.mp3"
 },
 "Atlantic Ocean": {
  "w": "17-w-atlantic-ocean.mp3",
  "s": "17-s-atlantic-ocean.mp3"
 },
 "Indian Ocean": {
  "w": "18-w-indian-ocean.mp3",
  "s": "18-s-indian-ocean.mp3"
 },
 "Arctic Ocean": {
  "w": "19-w-arctic-ocean.mp3",
  "s": "19-s-arctic-ocean.mp3"
 },
 "Southern Ocean": {
  "w": "20-w-southern-ocean.mp3",
  "s": "20-s-southern-ocean.mp3"
 },
 "Mediterranean Sea": {
  "w": "21-w-mediterranean-sea.mp3",
  "s": "21-s-mediterranean-sea.mp3"
 },
 "Red Sea": {
  "w": "22-w-red-sea.mp3",
  "s": "22-s-red-sea.mp3"
 },
 "Black Sea": {
  "w": "23-w-black-sea.mp3",
  "s": "23-s-black-sea.mp3"
 },
 "Caspian Sea": {
  "w": "24-w-caspian-sea.mp3",
  "s": "24-s-caspian-sea.mp3"
 },
 "Baltic Sea": {
  "w": "25-w-baltic-sea.mp3",
  "s": "25-s-baltic-sea.mp3"
 },
 "North Sea": {
  "w": "26-w-north-sea.mp3",
  "s": "26-s-north-sea.mp3"
 },
 "Caribbean Sea": {
  "w": "27-w-caribbean-sea.mp3",
  "s": "27-s-caribbean-sea.mp3"
 },
 "Arabian Sea": {
  "w": "28-w-arabian-sea.mp3",
  "s": "28-s-arabian-sea.mp3"
 },
 "South China Sea": {
  "w": "29-w-south-china-sea.mp3",
  "s": "29-s-south-china-sea.mp3"
 },
 "Strait of Gibraltar": {
  "w": "30-w-strait-of-gibraltar.mp3",
  "s": "30-s-strait-of-gibraltar.mp3"
 },
 "Strait of Malacca": {
  "w": "31-w-strait-of-malacca.mp3",
  "s": "31-s-strait-of-malacca.mp3"
 },
 "English Channel": {
  "w": "32-w-english-channel.mp3",
  "s": "32-s-english-channel.mp3"
 },
 "Bering Strait": {
  "w": "33-w-bering-strait.mp3",
  "s": "33-s-bering-strait.mp3"
 },
 "Strait of Hormuz": {
  "w": "34-w-strait-of-hormuz.mp3",
  "s": "34-s-strait-of-hormuz.mp3"
 },
 "Gulf of Mexico": {
  "w": "35-w-gulf-of-mexico.mp3",
  "s": "35-s-gulf-of-mexico.mp3"
 },
 "Persian Gulf": {
  "w": "36-w-persian-gulf.mp3",
  "s": "36-s-persian-gulf.mp3"
 },
 "Gulf of Guinea": {
  "w": "37-w-gulf-of-guinea.mp3",
  "s": "37-s-gulf-of-guinea.mp3"
 },
 "Gulf of Alaska": {
  "w": "38-w-gulf-of-alaska.mp3",
  "s": "38-s-gulf-of-alaska.mp3"
 },
 "Bay of Bengal": {
  "w": "39-w-bay-of-bengal.mp3",
  "s": "39-s-bay-of-bengal.mp3"
 },
 "Antarctica": {
  "w": "40-w-antarctica.mp3",
  "s": "40-s-antarctica.mp3"
 },
 "Oceania": {
  "w": "41-w-oceania.mp3",
  "s": "41-s-oceania.mp3"
 },
 "microscopic marine plants": {
  "w": "42-w-microscopic-marine-plants.mp3",
  "s": "42-s-microscopic-marine-plants.mp3"
 },
 "microorganisms": {
  "w": "43-w-microorganisms.mp3",
  "s": "43-s-microorganisms.mp3"
 },
 "chronological order": {
  "w": "44-w-chronological-order.mp3",
  "s": "44-s-chronological-order.mp3"
 },
 "flashback": {
  "w": "45-w-flashback.mp3",
  "s": "45-s-flashback.mp3"
 },
 "in medias res": {
  "w": "46-w-in-medias-res.mp3",
  "s": "46-s-in-medias-res.mp3"
 },
 "non-linear": {
  "w": "47-w-non-linear.mp3",
  "s": "47-s-non-linear.mp3"
 },
 "Ordovician-Silurian extinction": {
  "w": "48-w-ordovician-silurian-extinction.mp3",
  "s": "48-s-ordovician-silurian-extinction.mp3"
 },
 "Late Devonian extinction": {
  "w": "49-w-late-devonian-extinction.mp3",
  "s": "49-s-late-devonian-extinction.mp3"
 },
 "Permian-Triassic extinction": {
  "w": "50-w-permian-triassic-extinction.mp3",
  "s": "50-s-permian-triassic-extinction.mp3"
 },
 "The Great Dying": {
  "w": "51-w-the-great-dying.mp3",
  "s": "51-s-the-great-dying.mp3"
 },
 "Triassic-Jurassic extinction": {
  "w": "52-w-triassic-jurassic-extinction.mp3",
  "s": "52-s-triassic-jurassic-extinction.mp3"
 },
 "Cretaceous-Paleogene extinction": {
  "w": "53-w-cretaceous-paleogene-extinction.mp3",
  "s": "53-s-cretaceous-paleogene-extinction.mp3"
 },
 "Ordovician": {
  "w": "54-w-ordovician.mp3",
  "s": "54-s-ordovician.mp3"
 },
 "Devonian": {
  "w": "55-w-devonian.mp3",
  "s": "55-s-devonian.mp3"
 },
 "Permian": {
  "w": "56-w-permian.mp3",
  "s": "56-s-permian.mp3"
 },
 "Triassic": {
  "w": "57-w-triassic.mp3",
  "s": "57-s-triassic.mp3"
 },
 "Cretaceous": {
  "w": "58-w-cretaceous.mp3",
  "s": "58-s-cretaceous.mp3"
 },
 "morning light": {
  "w": "59-w-morning-light.mp3",
  "s": "59-s-morning-light.mp3"
 },
 "cairn": {
  "w": "60-w-cairn.mp3",
  "s": "60-s-cairn.mp3"
 },
 "ridge": {
  "w": "61-w-ridge.mp3",
  "s": "61-s-ridge.mp3"
 },
 "shrub": {
  "w": "62-w-shrub.mp3",
  "s": "62-s-shrub.mp3"
 }
};
