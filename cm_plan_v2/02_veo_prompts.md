# 動画生成AI（Veo / Veo 3 / Sora 等）用プロンプト集

各カットを個別生成し、編集ソフトで結合する前提。
すべて 16:9 / 24fps / シネマティック・ルック。

---

## 共通スタイル指定（全カット冒頭に付与）

```
Style: Cinematic Japanese TV commercial, shallow depth of field,
soft natural lighting, warm-yet-clean color grade, 24fps, 16:9,
photorealistic, subtle film grain, professional educational tone.
No text overlays in the generated video (text will be added in post).
```

---

## 🎬 Cut 1 — 0:00–0:04｜「常識への問い」

```
A 9-year-old Japanese boy sits alone in a dimly lit study room at night,
mechanically tapping a tablet showing math drills. His face is expressionless,
slightly tired. Cool blue desk-lamp lighting from the side. Camera slowly
pushes in on his blank eyes. Shallow depth of field. The atmosphere feels
slightly cold and isolating. Duration: 4 seconds. No on-screen text.
```

---

## 🎬 Cut 2 — 0:04–0:10｜「fMRI風・脳の発火演出」

```
Close-up of small hands flicking the beads of a traditional Japanese soroban
abacus on a wooden school desk. As the beads click, a translucent cyan
neural network visualization rises from the child's head, with the prefrontal
cortex glowing brightest, like an fMRI brain-activity map. Particles of light
flow along synapses. Background softly defocused. Scientific yet warm.
Duration: 6 seconds. Cinematic, photorealistic with VFX overlay.
No on-screen text.
```

---

## 🎬 Cut 3 — 0:10–0:17｜「Brain OS Update ビジュアル」

```
The cyan neural network from the previous shot smoothly morphs into a
sleek smartphone-style OS update interface floating in mid-air. A clean
minimal progress bar fills from 0% to 87%, surrounded by soft particles
and faint Japanese-inspired geometric patterns. Background: deep navy
gradient with subtle starfield. The mood is futuristic, premium, hopeful.
Duration: 7 seconds. No on-screen text — leave clean negative space in
the center for post-production typography.
```

---

## 🎬 Cut 4 — 0:17–0:23｜「忍耐力・教室シーン」

```
Inside a bright, friendly Japanese soroban classroom in the afternoon.
A 10-year-old girl, ponytail, wearing a simple cardigan, frowns slightly
at a wrong answer, takes a deep breath, then resets the abacus and tries
again with focused determination. A kind female teacher in her 40s nods
approvingly in the soft-focus background. Warm golden-hour light streams
through tall windows. Emotional, documentary-style, handheld subtle motion.
Duration: 6 seconds. No on-screen text.
```

---

## 🎬 Cut 5 — 0:23–0:27｜「彦根城・地域密着」

```
Wide cinematic shot of Hikone Castle in Shiga, Japan, glowing in warm
sunset light. In the foreground, a small group of elementary school
children carrying soroban cases walk out of a neighborhood classroom,
laughing. One child high-fives a waiting parent. Cherry-blossom petals
drift gently. Lens flare, golden hour, nostalgic and hopeful tone.
Duration: 4 seconds. No on-screen text.
```

---

## 🎬 Cut 6 — 0:27–0:30｜「CTA背景」

```
Minimalist clean background: soft pale blue gradient with very subtle
floating light particles. Center area intentionally empty for logo, QR
code, and Japanese typography to be added in post-production. Calm,
trustworthy, premium educational brand feel. Duration: 3 seconds.
No on-screen text.
```

---

## 生成時の注意事項
1. **テキストはAIに描かせない**：日本語フォントの破綻防止。すべてAfter Effects / Premiere で重ねる。
2. **同一児童の一貫性**：Cut 1とCut 4で別人物にする（前=孤独な学習、後=仲間と学ぶそろばん）ことで対比を明確化。
3. **fMRI演出の倫理**：「医学的fMRI画像」と誤認されないよう、青い粒子＝抽象表現に留める。
4. **彦根城**：実写優先。Veo出力は参考用、本番はドローン実写を推奨。
5. **音声**：Veo出力にナレは入れない。日本語ナレーション・BGMはポストで合成。
