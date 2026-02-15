# Seren Matcha - Shopify Implementation Guide

**Date:** February 15, 2026  
**Mock-up Location:** `/home/openclaw/.openclaw/workspace/seren-mockup/`  
**Target Theme:** Palo Alto (Rocky's Matcha uses this)  

---

## 🎯 Quick Start

1. **View Mock-Up:** Open `index.html` and `product-page-example.html` in browser
2. **Review Features:** Read this guide
3. **Purchase Theme:** Buy Palo Alto from Shopify Theme Store ($350 USD)
4. **Install Apps:** See recommended apps below
5. **Customize:** Follow step-by-step below

---

## 📦 Palo Alto Theme - What's Included vs What We Need

### ✅ Palo Alto Native Features (Out of Box)

| Feature | Status | Notes |
|---------|--------|-------|
| Mobile responsive | ✅ Included | Excellent mobile-first design |
| Sticky navigation | ✅ Included | Nav stays at top on scroll |
| Mega menu | ✅ Included | For "Curated Brands" section |
| Product quick view | ✅ Included | Add to cart from collection page |
| Image zoom | ✅ Included | Hover to zoom product photos |
| Color/variant swatches | ✅ Included | For size options (30g, 100g) |
| Product recommendations | ✅ Included | "You may also like" |
| Cart drawer | ✅ Included | Slide-out cart |
| Instagram feed | ✅ Included | Built-in integration |
| Product filtering | ✅ Included | Filter by brand, price, etc. |
| Search | ✅ Included | Predictive search |
| Blog | ✅ Included | For education content |
| Newsletter popup | ✅ Included | Email capture |

### ❌ Features We Need to Add (Apps or Custom)

| Feature | Solution | Cost | Priority |
|---------|----------|------|----------|
| **Subscriptions** | ReCharge app | $99/mo (0-500 subs) | 🔴 Critical |
| **Waitlist capture** | Back in Stock app | $19/mo | 🔴 Critical |
| **Product reviews** | Judge.me | Free plan OK | 🔴 Critical |
| **Countdown timers** | Hurrify app | $9.99/mo | 🟡 High |
| **Flavor profiling** | Custom metafields | Free (manual) | 🟡 High |
| **Email marketing** | Klaviyo | Free <250 contacts | 🔴 Critical |
| **Loyalty program** | Smile.io | $49/mo | 🟢 Medium |
| **Afterpay** | Shopify Payments | Free | 🔴 Critical |
| **Matcha quiz** | Octane AI | $50/mo | 🟢 Medium |
| **Bundle builder** | Bold Bundles | $19.99/mo | 🟢 Medium |

**Total Monthly App Costs (Minimum):** ~$165/mo  
**Total Monthly App Costs (Full Stack):** ~$285/mo

---

## 🚀 Phase-by-Phase Implementation

### PHASE 1: Foundation (Week 1) - GET LIVE FAST

**Goal:** Basic functioning store with Seren products

#### Day 1-2: Shopify Setup
- [ ] Purchase Shopify plan (Basic $39/mo recommended to start)
- [ ] Buy Palo Alto theme ($350 one-time)
- [ ] Install theme
- [ ] Set up domain (serenmatcha.com.au or keep serendipityau.com)
- [ ] Configure shipping zones (Australia + international)
- [ ] Enable Shopify Payments + Afterpay

#### Day 3-4: Product Upload
- [ ] Upload Seren products (Haru, Hikari, coming soon items)
- [ ] Create product descriptions (copy from mock-up)
- [ ] Add product photos (white background + lifestyle)
- [ ] Set up variants (30g, 100g sizes)
- [ ] Create "coming soon" products (Mie, Akari) with $0 price

#### Day 5-7: Theme Customization
- [ ] Update colors to match brand (use mock-up CSS variables)
- [ ] Upload logo
- [ ] Configure navigation menu:
  - Seren Matcha (featured)
  - Limited Edition
  - Starter Kits
  - Curated Brands (mega menu with 15 brands)
  - Education
  - Wholesale
- [ ] Set up homepage sections:
  - Hero banner (use mock-up copy)
  - Featured collection (Seren products)
  - Starter kits
  - Instagram feed
- [ ] Configure footer
- [ ] Create "Our Story" page
- [ ] Create "FAQ" page

**✅ Checkpoint:** Store is live and functional, can process orders

---

### PHASE 2: Core Features (Week 2-3) - ADD POWER

#### Week 2: Subscriptions & Reviews

**Subscription Setup (ReCharge)**
- [ ] Install ReCharge app ($99/mo)
- [ ] Connect to Shopify products
- [ ] Configure subscription options:
  - Delivery frequencies: 2, 4, 6, 8 weeks
  - Discount: 15% off
  - Default frequency: 4 weeks
- [ ] Customize subscription widget on product pages
- [ ] Set up customer portal (manage subscriptions)
- [ ] Create welcome email sequence for subscribers
- [ ] Test subscription checkout flow

**Reviews Setup (Judge.me)**
- [ ] Install Judge.me app (free plan)
- [ ] Import any existing reviews (if any)
- [ ] Configure review request emails (7 days after delivery)
- [ ] Add review widgets to:
  - Product pages (below title)
  - Homepage (social proof section)
  - Collection pages (star ratings)
- [ ] Customize review form (add photo upload)
- [ ] Seed with 10-20 initial reviews (ask early customers)

#### Week 3: Email Marketing & Waitlist

**Email Marketing (Klaviyo)**
- [ ] Install Klaviyo app (free <250 contacts)
- [ ] Set up welcome flow:
  - Email 1: Welcome + 10% off (immediate)
  - Email 2: Education about matcha (Day 2)
  - Email 3: University partnerships story (Day 5)
  - Email 4: Customer reviews (Day 7)
- [ ] Create abandoned cart flow:
  - Email 1: "You left matcha behind" (1 hour)
  - Email 2: "Still thinking?" + testimonial (24 hours)
  - Email 3: "Last chance" + 5% off (48 hours)
- [ ] Set up post-purchase flow:
  - Email 1: Order confirmation tips (immediate)
  - Email 2: How to prepare (Day 1)
  - Email 3: Request review (Day 7)
  - Email 4: Reorder reminder (Day 25)

**Waitlist Capture (Back in Stock)**
- [ ] Install Back in Stock app ($19/mo)
- [ ] Enable on sold-out products (Mie, Akari coming soon items)
- [ ] Customize waitlist button ("Join Waitlist")
- [ ] Set up notification email when back in stock
- [ ] Add waitlist count display ("1,200+ on waitlist")

**✅ Checkpoint:** Subscriptions working, reviews live, emails automated

---

### PHASE 3: Conversion Optimization (Week 4) - MAXIMIZE SALES

#### Limited Edition Section

**Custom Section Creation**
- [ ] Create "Limited Edition" section in theme customizer
- [ ] Add Natsu Limited Release banner
- [ ] Install Hurrify app for countdown timer ($9.99/mo)
- [ ] Configure timer (end date, styling)
- [ ] Add scarcity messaging ("Only 150 tins")
- [ ] Create pre-order product (if launching before stock arrives)

#### Starter Kits / Bundles

**Bundle Products**
- [ ] Create bundle products manually, OR
- [ ] Install Bold Bundles app ($19.99/mo) for dynamic bundles
- [ ] Set up 3 kits:
  - The Essentials ($85) - Haru + tools
  - The Complete Ritual ($139) - Haru + Hikari + ceremony tools
  - The Gift Set ($105) - Hikari + premium tools + gift box
- [ ] Add "Save $X" badges
- [ ] Create "build your own bundle" page (optional)

#### Trust & Social Proof

- [ ] Add trust badges to product pages:
  - "100% Ceremonial Grade"
  - "Free Shipping $99+"
  - "Afterpay Available"
  - "30-Day Satisfaction Guarantee"
- [ ] Add "Best Seller" badges (manual or app)
- [ ] Create "As Seen In" section (if any press)
- [ ] Add customer testimonials to homepage
- [ ] Display total customers served ("Trusted by 15,000+")

**✅ Checkpoint:** Store is optimized for maximum conversion

---

### PHASE 4: Advanced Features (Week 5-6) - SCALE & RETAIN

#### Loyalty Program (Smile.io)
- [ ] Install Smile.io app ($49/mo)
- [ ] Configure points system:
  - 1 point per $1 spent
  - 100 points = $5 discount
  - Bonus: 200 points for account creation
  - Bonus: 500 points for referral
- [ ] Create reward tiers (Bronze, Silver, Gold, Platinum)
- [ ] Add "Earn Points" section to product pages
- [ ] Create loyalty landing page

#### Matcha Quiz ("Find Your Match")
- [ ] Install Octane AI quiz app ($50/mo), OR
- [ ] Create manual quiz using Typeform ($25/mo), OR
- [ ] Build custom quiz page (free, more work)
- [ ] Quiz questions:
  1. How do you typically drink matcha? (Latte, Traditional, Cold brew)
  2. What flavor profile do you prefer? (Sweet, Umami, Balanced, Bold)
  3. When do you drink matcha? (Morning, Afternoon, Evening)
  4. Experience level? (Beginner, Intermediate, Expert)
- [ ] Map answers to products:
  - Sweet + Latte + Beginner = Haru
  - Bold + Traditional + Expert = Hikari
  - Coming soon options = Join waitlist
- [ ] Add quiz CTA to homepage hero
- [ ] Add quiz link to navigation

#### Flavor Profiling (Custom Metafields)
- [ ] Create custom metafields in Shopify:
  - `flavor.sweetness` (integer 1-100)
  - `flavor.umami` (integer 1-100)
  - `flavor.creaminess` (integer 1-100)
  - `flavor.bitterness` (integer 1-100)
- [ ] Add metafield values to each product
- [ ] Customize product template to display flavor bars (use mock-up CSS)
- [ ] Add flavor tags (Sweet, Creamy, Umami, etc.)

#### Wholesale Portal
- [ ] Install Wholesale Club app ($49/mo), OR
- [ ] Create manual wholesale page with form
- [ ] Set up wholesale pricing tiers:
  - 5-10 tins: 15% off
  - 11-20 tins: 25% off
  - 21+ tins: 35% off
- [ ] Create wholesale inquiry form
- [ ] Build wholesale landing page with:
  - Cafe partnership info
  - University partnership program
  - Sample request option

**✅ Checkpoint:** Full-featured store with retention + B2B

---

### PHASE 5: Content & SEO (Week 7) - GET FOUND

#### Blog & Education
- [ ] Create blog categories:
  - Matcha Education
  - Recipes
  - Preparation Guides
  - Our Story
  - University Partnerships
- [ ] Write 5 initial blog posts:
  1. "What is Ceremonial Grade Matcha?"
  2. "How to Prepare the Perfect Bowl of Matcha"
  3. "Seren Matcha vs Coffee: The Third Wave Shift"
  4. "Understanding Cultivars: Saemidori vs Yutakamidori"
  5. "Meet Our University Partners"
- [ ] Optimize posts for SEO:
  - Keywords: "ceremonial matcha australia", "best matcha sydney", "buy matcha online"
  - Meta descriptions
  - Alt text on images

#### SEO Optimization
- [ ] Install Plug in SEO app (free plan)
- [ ] Optimize product pages:
  - Title tags: "[Product] - Ceremonial Matcha | Seren Matcha"
  - Meta descriptions (155 chars)
  - URL structure: /products/haru-ceremonial-matcha
  - Image alt text
- [ ] Create XML sitemap (automatic in Shopify)
- [ ] Submit to Google Search Console
- [ ] Set up Google Analytics 4
- [ ] Configure Facebook Pixel (for ads later)

#### University Partnership Pages
- [ ] Create "University Partners" landing page
- [ ] List 4 universities with logos
- [ ] Explain partnership benefits:
  - Free workshops
  - Student discounts
  - Campus pop-ups
  - Research collaboration
- [ ] Add student verification form (SheerID app)
- [ ] Create 15% student discount code

**✅ Checkpoint:** Content-rich site with strong SEO foundation

---

### PHASE 6: Launch Preparation (Week 8) - GO LIVE

#### Pre-Launch Checklist
- [ ] Test all user flows:
  - Browse → Add to Cart → Checkout (one-time)
  - Browse → Subscribe → Checkout
  - Join waitlist → Receive notification
  - Write review → Earn loyalty points
  - Complete quiz → Receive recommendation
- [ ] Test on mobile devices (iOS Safari, Android Chrome)
- [ ] Check page load speed (aim for <3 seconds)
- [ ] Proofread all copy
- [ ] Verify all links work
- [ ] Test email flows (welcome, abandoned cart, post-purchase)
- [ ] Set up customer service channels:
  - Support email (hello@serenmatcha.com.au)
  - WhatsApp Business (optional)
  - Live chat (Tidio app - free plan)

#### Soft Launch (Week 8)
- [ ] Announce to email list (if any existing)
- [ ] Post on @serendipityaustralia Instagram
- [ ] Offer launch discount (15% off first order)
- [ ] Set launch stock limits (create scarcity)
- [ ] Monitor orders/traffic in real-time
- [ ] Respond to all customer inquiries within 2 hours

#### Grand Launch (Week 9)
- [ ] Press outreach (Australian food/lifestyle blogs)
- [ ] Instagram influencer seeding (send free samples)
- [ ] University campus activations
- [ ] Paid ads:
  - Facebook/Instagram ($500 budget)
  - Google Shopping ($300 budget)
- [ ] Monitor and optimize daily

**✅ Checkpoint:** Store is live, generating revenue, iterating based on feedback

---

## 💰 Cost Summary

### One-Time Costs
- Shopify theme (Palo Alto): $350
- Product photography: $500-1,500 (if hiring)
- Logo/branding (if new): $0-500
- **Total One-Time:** $850-2,350

### Monthly Recurring Costs
- Shopify Basic plan: $39
- ReCharge (subscriptions): $99
- Klaviyo (email): $0-20 (free <250 contacts)
- Judge.me (reviews): $0-15 (free plan OK)
- Back in Stock (waitlist): $19
- Hurrify (countdown): $10
- Smile.io (loyalty): $49 (optional)
- Octane AI (quiz): $50 (optional)
- Bold Bundles: $20 (optional)
- **Total Monthly (Minimum):** $167
- **Total Monthly (Full Stack):** $306

### First Year Projection
- Setup costs: $1,000-2,500
- Monthly ops (12 months): $2,000-3,700
- **Total Year 1:** $3,000-6,200

---

## 📊 Success Metrics (6 Months Post-Launch)

### Traffic
- Target: 10,000 monthly visitors
- Sources: 40% organic, 30% social, 20% direct, 10% paid

### Conversion
- Overall conversion rate: 2-3%
- Subscription adoption: 20% of first orders
- Email capture rate: 15%
- Average order value: $80-120

### Revenue Split (Goal)
- Seren products: 40% of revenue (up from 10%)
- Curated brands: 60% of revenue
- Subscriptions: 30% of total orders

### Brand Growth
- Instagram: 15k → 25k followers
- Email list: 5,000+ subscribers
- Product reviews: 200+ reviews average 4.8★
- Returning customer rate: 30%

---

## 🎨 Brand Assets Needed from Kevin

### Photography
- [ ] **Product photos** (white background, 4 angles each):
  - Haru tin (front, back, top, angled)
  - Hikari tin (front, back, top, angled)
  - Coming soon tins (Mie, Akari) - mockups OK
  - Accessories (whisk, bowl, scoop, sifter)
- [ ] **Lifestyle photos:**
  - Matcha being prepared (hands whisking)
  - Morning scene with matcha and light
  - Latte being poured
  - Person enjoying matcha (Sydney/Melbourne scene)
  - University campus activation photos
  - Group of friends drinking matcha
- [ ] **Detail shots:**
  - Matcha powder close-up (vibrant green)
  - Whisking action (froth forming)
  - Matcha tin with Japanese aesthetic
  - Ingredients/farm photos (if available)

### Content
- [ ] **Social media posts** (for color palette):
  - Send 5-10 recent Instagram posts
  - Brand aesthetic examples
  - Preferred color scheme
- [ ] **Copy refinement:**
  - Brand story (founder narrative? why start Seren?)
  - Product tasting notes (expand beyond current)
  - University partnership details
  - Customer testimonials (if any)

### Brand Guidelines (if exist)
- [ ] Logo files (SVG, PNG)
- [ ] Color codes (hex values)
- [ ] Font files (if custom)
- [ ] Brand voice/tone guide

---

## 🔥 Quick Wins (Do These First!)

1. **Best-seller badge on Haru** - Social proof drives sales
2. **Subscribe & Save 15%** - Recurring revenue = predictable cash flow
3. **Waitlist for sold-out items** - Capture demand, build hype
4. **Email capture popup** - Build list from day 1
5. **Free shipping threshold at $99** - Increase AOV
6. **Afterpay** - Remove price barrier (43% higher conversion)
7. **Reviews on product pages** - Trust = sales
8. **Instagram feed on homepage** - Fresh content, social proof
9. **"Our Story" page** - Third wave positioning
10. **Limited edition with timer** - FOMO drives urgency

---

## 🚨 Common Mistakes to Avoid

1. **Don't bury Seren products** - Lead with own brand, not curated brands
2. **Don't skip mobile testing** - 70% of traffic will be mobile
3. **Don't launch without email capture** - Build list from day 1
4. **Don't ignore page speed** - Slow = lost sales
5. **Don't skip reviews** - Trust signals are critical
6. **Don't forget subscription option** - Recurring revenue is gold
7. **Don't make navigation confusing** - Clear path to Seren products
8. **Don't use stock photos** - Authenticity matters
9. **Don't launch without analytics** - Can't improve what you don't measure
10. **Don't forget to test checkout** - Broken checkout = $0 revenue

---

## 🎯 Next Steps for Kevin

1. **Send social media posts** - I'll update color palette
2. **Review mock-up** - Open `index.html` and `product-page-example.html`
3. **Decide on theme** - Buy Palo Alto or go custom?
4. **Schedule photoshoot** - Need product + lifestyle shots
5. **Purchase apps** - Start with essentials (ReCharge, Klaviyo, Judge.me)
6. **Set launch date** - Work backward for timeline

---

**Questions? Issues? Need help?**

I'll be monitoring competitor websites daily starting tomorrow at 9 AM AEDT. Any changes they make, I'll catch and we can adapt.

Let's dominate the third wave. 🍵

**Built by OpenClaw - February 2026**
