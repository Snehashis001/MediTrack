/* ==========================================================================
   MediTrack - Clinical Categories & Fallback Product Catalog
   ========================================================================== */
const CATEGORIES = [
  { name: 'Pain Relief', icon: '💊', count: 3 },
  { name: 'Vitamins', icon: '🍊', count: 3 },
  { name: 'Personal Care', icon: '🧴', count: 2 },
  { name: 'Healthcare Devices', icon: '🩺', count: 3 },
  { name: 'First Aid', icon: '🩹', count: 2 },
  { name: 'General Wellness', icon: '🌿', count: 3 }
];

const RAW_CATALOG = [
  '1|Paracetamol Extra 500mg|Acetaminophen|Pain Relief|6.49|8.99|28|20 Tablets|4.9|0|https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=600&q=80|Fast relief for mild fever and headaches.|1',
  '2|Ibuprofen Ultra Softgels 400mg|Ibuprofen NSAID|Pain Relief|9.99|12.99|23|30 Softgels|4.8|0|https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=600&q=80|Anti-inflammatory for joint stiffness.|1',
  '3|Diclofenac Relief Gel|Diclofenac Sodium 1%|Pain Relief|7.50|9.50|21|50g Tube|4.7|0|https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=600&q=80|Deep-penetrating topical pain gel.|0',
  '4|Vitamin C + Zinc Immunity Fizz|Ascorbic Acid + Zinc|Vitamins|8.99|11.99|25|20 Tablets|4.9|0|https://images.unsplash.com/photo-1577401239170-897942555fb3?auto=format&fit=crop&w=600&q=80|Effervescent antioxidant immune booster.|1',
  '5|Vitamin D3 2000 IU + K2|Cholecalciferol + K2|Vitamins|14.50|18.00|19|60 Softgels|4.8|0|https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&w=600&q=80|Bone density and cardiovascular support.|0',
  '6|Omega-3 Triple Strength Fish Oil|EPA 600mg + DHA 400mg|Vitamins|16.99|22.00|23|60 Softgels|4.9|0|https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=600&q=80|Molecularly distilled fish oil for heart.|1',
  '7|Ceramide Hydrating Daily Cleanser|Ceramides 1, 3, 6-II|Personal Care|13.25|16.50|20|250ml Pump|4.9|0|https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80|Gentle moisturizing wash for skin barrier.|1',
  '8|Medicated Antiseptic Lip Balm SPF 15|Camphor + Menthol|Personal Care|4.25|5.50|23|10g Tube|4.6|0|https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=600&q=80|Intense cooling relief for chapped lips.|0',
  '9|Digital Smart BP Monitor|Oscillometric Upper Arm|Healthcare Devices|34.99|45.00|22|1 Unit + Cuff|4.8|0|https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=600&q=80|Accurate one-touch blood pressure monitor.|1',
  '10|Infrared Forehead Thermometer|Dual Mode Sensor|Healthcare Devices|22.50|29.99|25|1 Unit|4.7|0|https://images.unsplash.com/photo-1584017911766-d451b3d0e843?auto=format&fit=crop&w=600&q=80|1-second touch-free reading with fever alert.|0',
  '11|Fingertip Pulse Oximeter Pro|SpO2 Sensor|Healthcare Devices|18.99|24.99|24|1 Device|4.8|0|https://images.unsplash.com/photo-1603398938378-e54eab446dde?auto=format&fit=crop&w=600&q=80|OLED display showing oxygen saturation & pulse.|0',
  '12|Waterproof Antiseptic Bandages|Sterile Fabric Adhesive|First Aid|5.99|7.50|20|Box of 50|4.8|0|https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=600&q=80|Water-resistant flexible adhesive strips.|0',
  '13|Povidone-Iodine Solution 10%|Povidone-Iodine USP|First Aid|6.80|8.50|20|100ml Bottle|4.7|0|https://images.unsplash.com/photo-1584362917165-526a968579e8?auto=format&fit=crop&w=600&q=80|Broad-spectrum antiseptic solution for cuts.|0',
  '14|Melatonin 5mg Sleep Gummies|Melatonin + Chamomile|General Wellness|11.99|15.00|20|60 Gummies|4.9|0|https://images.unsplash.com/photo-1576602976047-174e57a47881?auto=format&fit=crop&w=600&q=80|Botanical sleep aid for restful nights.|1',
  '15|Organic Ashwagandha KSM-66|Withania Somnifera|General Wellness|15.50|19.99|22|60 Veg Caps|4.8|0|https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80|Natural adaptogen for stress resilience.|0',
  '16|Amoxicillin Clavulanate 625mg|Amoxicillin + Clavulanic|General Wellness|14.20|18.00|21|10 Tablets|4.9|1|https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=600&q=80|PRESCRIPTION REQUIRED: Antibacterial therapy.|1'
];

const FALLBACK_PRODUCTS = RAW_CATALOG.map((item) => {
  const p = item.split('|');
  return {
    id: parseInt(p[0], 10),
    name: p[1],
    generic_name: p[2],
    category: p[3],
    price: parseFloat(p[4]),
    mrp: parseFloat(p[5]),
    discount: parseInt(p[6], 10),
    dosage: p[7],
    rating: parseFloat(p[8]),
    requires_prescription: parseInt(p[9], 10),
    image_url: p[10],
    description: p[11],
    is_bestseller: parseInt(p[12], 10)
  };
});
