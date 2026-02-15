# Seren Matcha Website Mock-Up

**Created:** February 15, 2026  
**Purpose:** Visualization for Shopify redesign  
**Approach:** Seren-First (Option A)  
**Theme Reference:** Palo Alto (Rocky's Matcha)

---

## 🎯 Design Philosophy

**"The Third Wave of Matcha"**

This mock-up implements a Seren-first approach while maintaining secondary access to curated brands. The design focuses on:

1. **Brand clarity** - Seren front and center
2. **Modern minimalism** - Clean Japanese aesthetic meets Australian lifestyle
3. **Conversion optimization** - Best practices from all 6 competitors
4. **Educational focus** - Leveraging university partnerships
5. **Community building** - Social proof and engagement

---

## 📂 File Structure

```
seren-mockup/
├── index.html          # Main homepage
├── css/
│   └── styles.css      # All styling (Palo Alto inspired)
├── js/
│   └── main.js         # Interactive features
└── README.md           # This file
```

---

## 🚀 How to Use

### View the Mock-Up

1. Open `index.html` in any web browser
2. Or run a local server:
   ```bash
   cd /home/openclaw/.openclaw/workspace/seren-mockup
   python3 -m http.server 8000
   # Then visit: http://localhost:8000
   ```

### Next Steps

1. **Add real images** - Replace placeholders with actual product photos
2. **Adjust colors** - Update CSS variables based on social media posts
3. **Review content** - Edit copy to match brand voice
4. **Choose Shopify theme** - Palo Alto or custom build
5. **Implement features** - See checklist below

---

## ✨ Key Features Implemented

### Homepage Sections

✅ **Hero Section**
- "Third Wave of Matcha" positioning
- Dual CTA (Shop / Find Your Match)
- Social proof (15k followers, 350 tins sold, university partnerships)

✅ **Featured Collection (Seren Products)**
- 4 product cards: Haru, Hikari, Mie (coming soon), Akari (coming soon)
- Best-seller badges
- Flavor tags (Sweet, Creamy, Umami, etc.)
- Subscribe & Save option (15% off)
- Waitlist buttons for unavailable products
- Coming soon indicators with waitlist count

✅ **Limited Edition Section**
- "Memories of Summer 2026" - Natsu release
- Countdown timer (days/hours/minutes)
- Stock scarcity messaging ("Only 150 tins")
- Pre-order CTA

✅ **Starter Kits**
- 3 bundles: Essentials ($85), Complete Ritual ($139), Gift Set ($105)
- "Most Popular" badge on featured kit
- Value comparison (was/now/save)

✅ **Education Section**
- University partnership highlight
- 4 unique value propositions
- Secondary CTA for partner program

✅ **Our Story**
- Third wave positioning explained
- Brand philosophy
- Stats showcase (15k community, 4 universities, 350 tins, 1,200 waitlist)

✅ **Curated Brands**
- Secondary section for other brands
- 4 featured: Marukyu Koyamaen, Ippodo, Horii Shichimeien, Kanbayashi Shunsho
- Link to full collection

✅ **Instagram Feed**
- @serendipityaustralia integration point
- "Join 15k+ matcha lovers" messaging

✅ **Footer**
- Comprehensive navigation
- Afterpay mention
- Free shipping highlight

---

## 🎨 Design System

### Colors (Update based on social posts Kevin sends)

```css
--color-primary: #2C5F2D;         /* Deep green */
--color-primary-light: #97BC62;   /* Soft sage */
--color-secondary: #F5F5DC;       /* Cream/beige */
--color-accent: #D4AF37;          /* Gold */
```

### Typography

- **Primary:** Inter (clean, modern san-serif)
- **Display:** Crimson Pro (elegant serif for headings)

### Spacing

- Consistent rhythm: 0.5rem, 1rem, 2rem, 4rem, 6rem
- Mobile-first responsive

---

## 🏆 Competitive Features Integrated

### From Anya Matcha
- ✅ Limited edition releases ("Memories of Season")
- ✅ Flavor profiling (tags on products)
- ✅ Best-seller labeling
- ✅ Afterpay mention
- ✅ Sale timer for urgency

### From Matcha Society
- ✅ Bundle strategy ($66-165 range)
- ✅ CSR angle (can add 1% to charity)
- ✅ Seasonal releases

### From Rocky's Matcha
- ✅ Wide product range (coming soon items)
- ✅ Single cultivar storytelling
- ✅ Premium/entry tier distinction
- ✅ Palo Alto theme aesthetic

### From Xundays
- ✅ Community positioning
- ✅ Product launch announcements

---

## 📋 Shopify Implementation Checklist

### Must-Have Features

**Product Features**
- [ ] Subscription engine (ReCharge or similar)
- [ ] Waitlist email capture (Back in Stock app)
- [ ] Low stock badges (< 10 remaining)
- [ ] "Recently viewed" products
- [ ] Product reviews (Judge.me or Loox)
- [ ] Flavor profiling graphs (custom or Metafields)
- [ ] Cultivar education popups

**Site Features**
- [ ] Limited edition countdown timer (real backend)
- [ ] Instagram feed integration (Instafeed.js)
- [ ] Email popup (Klaviyo)
- [ ] Matcha quiz ("Find Your Match")
- [ ] Afterpay integration
- [ ] Loyalty program (Smile.io or LoyaltyLion)
- [ ] Wholesale portal (separate login)

**Marketing Features**
- [ ] Exit-intent popup
- [ ] Abandoned cart emails
- [ ] Post-purchase upsell
- [ ] CSR partnership section (1% to cause)
- [ ] Referral program

**Content**
- [ ] Blog for education content
- [ ] University partnership landing page
- [ ] About Us / Our Story page
- [ ] FAQ page
- [ ] Matcha preparation guide
- [ ] Cultivar education page

---

## 🎭 Missing: Placeholder Content

Kevin needs to provide:

1. **Product Photos**
   - Haru, Hikari, Mie, Akari tins
   - Lifestyle shots (matcha being prepared, morning scenes)
   - Bundle/kit photos
   - White background + lifestyle variants

2. **Social Media Posts**
   - Recent Instagram posts for color palette
   - Content for IG feed section
   - Brand aesthetic examples

3. **Copy Refinement**
   - Product descriptions (expand current)
   - Tasting notes (detailed)
   - Brand story (founder narrative?)
   - Educational content

4. **Assets**
   - Logo (current Seren Matcha wordmark)
   - Icon set (if exists)
   - Brand guidelines (colors, fonts, tone)

---

## 🔧 Palo Alto Theme Capabilities

**What Palo Alto Includes:**
- ✅ Mobile-first responsive design
- ✅ Quick add to cart
- ✅ Product image zoom
- ✅ Color/variant swatches
- ✅ Instagram feed integration
- ✅ Product recommendations
- ✅ Sticky navigation
- ✅ Mega menu
- ✅ Filtering & search
- ✅ Cart drawer/popup

**What We Need to Add:**
- ❌ Subscription engine (3rd party app)
- ❌ Waitlist capture (3rd party app)
- ❌ Countdown timers (custom or app)
- ❌ Limited edition sections (custom blocks)
- ❌ Flavor profiling (custom metafields)
- ❌ University partnership section (custom)
- ❌ Matcha quiz (custom or app)

**Recommendation:** Start with Palo Alto theme + customizations. If limitations hit, consider:
- Turbo theme (more flexible)
- Dawn theme (Shopify default, highly customizable)
- Custom Liquid theme (full control)

---

## 💡 Additional Ideas Not Yet Implemented

1. **"Build Your Bundle" Tool**
   - Interactive bundle builder
   - Custom kit with 3-5 items
   - Savings calculator

2. **Matcha Passport**
   - Track matcha journey
   - Tasting notes for each blend
   - Gamification (badges for trying all blends)

3. **University Student Discount**
   - Verify .edu email
   - 15% off first order
   - Referral program for students

4. **Virtual Matcha Workshop**
   - Zoom/video sessions
   - Purchasable add-on
   - Partner with universities

5. **Seasonal Subscription Box**
   - Quarterly limited edition + accessories
   - "Memories of Each Season"

6. **Carbon Neutral Shipping**
   - Offset calculator at checkout
   - Sustainability messaging

---

## 🚀 Launch Roadmap Recommendation

### Phase 1: Foundation (Week 1-2)
- [ ] Purchase Palo Alto theme
- [ ] Set up Shopify store structure
- [ ] Upload product photos
- [ ] Configure payment (Afterpay)
- [ ] Set up shipping zones

### Phase 2: Core Features (Week 3-4)
- [ ] Install subscription app (ReCharge)
- [ ] Add waitlist capture
- [ ] Integrate reviews
- [ ] Build limited edition section
- [ ] Create starter kit bundles

### Phase 3: Marketing (Week 5-6)
- [ ] Email marketing (Klaviyo)
- [ ] Instagram feed integration
- [ ] Build matcha quiz
- [ ] Set up abandoned cart flows
- [ ] Create blog content

### Phase 4: Advanced (Week 7-8)
- [ ] Loyalty program
- [ ] Wholesale portal
- [ ] University partnership page
- [ ] Referral program
- [ ] Launch CSR partnership

### Phase 5: Launch (Week 9)
- [ ] Soft launch to email list
- [ ] Announce on Instagram
- [ ] University partner rollout
- [ ] Press outreach

---

## 📊 Success Metrics to Track

**Conversion:**
- Homepage → Product page: Target 40%+
- Product page → Add to cart: Target 5-8%
- Overall conversion rate: Target 2-3%

**Engagement:**
- Time on site: Target 3+ minutes
- Pages per session: Target 3+
- Bounce rate: Target < 50%

**Revenue:**
- Average order value: Target $80-120
- Subscription adoption: Target 20% of orders
- Bundle attachment rate: Target 30%

**Brand:**
- Seren products: Grow from 10% to 40% revenue in 6 months
- Instagram followers: Grow from 15k to 25k
- Email list: 5k+ subscribers

---

## 🎯 Seren vs Competitors Positioning

**Seren's Unique Value Proposition:**
> "The Third Wave of Matcha - Thoughtfully crafted ceremonial matcha from Uji, Kyoto, designed for modern Australian life. Partnered with 4 universities, trusted by 15k+ matcha lovers, and committed to education, accessibility, and quality without pretension."

**Vs Anya:** Less folklore/mystique, more modern/accessible  
**Vs Matcha Society:** Less B2B corporate, more community/education  
**Vs Rocky's:** Less ultra-premium, more everyday luxury  
**Vs Xundays:** Less cute branding, more sophisticated

---

## 🤝 Next Actions for Kevin

1. **Send social media posts** - for color palette refinement
2. **Provide product photos** - high-res, white background + lifestyle
3. **Review copy** - edit product descriptions, brand story
4. **Make strategic decision:**
   - Palo Alto theme + customizations? (recommended)
   - OR custom Liquid theme from scratch? (more work, full control)
5. **Choose apps:**
   - Subscription: ReCharge vs Bold vs native Shopify
   - Reviews: Judge.me vs Loox vs Stamped
   - Email: Klaviyo (recommended) vs Omnisend
6. **Set launch date** - work backward for timeline

---

**Built by OpenClaw AI - February 2026**  
*Competitor intel gathered, best practices integrated, ready to dominate the third wave.*
