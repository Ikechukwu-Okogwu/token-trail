# result_explanation

## Pair S01.zip,S02.zip
- Pair: `S01.zip,S02.zip`
- Testing: `cluster_consistency`
- Why expected label: both belong to the same Rank triple family with only ordering/identifier variation, so this pair is high.
- What engine should do: keep strong similarity for same-family variants.

## Pair S01.zip,S03.zip
- Pair: `S01.zip,S03.zip`
- Testing: `cluster_consistency`
- Why expected label: both are Rank triple members with method-order variation only, so this pair is high.
- What engine should do: preserve high similarity inside the intended triple cluster.

## Pair S01.zip,S04.zip
- Pair: `S01.zip,S04.zip`
- Testing: `family_separation`
- Why expected label: S01 is from the Rank triple family and S04 is from the PairHigh family, so this pair is low.
- What engine should do: keep different intent families separated.

## Pair S01.zip,S05.zip
- Pair: `S01.zip,S05.zip`
- Testing: `family_separation`
- Why expected label: S01 is Rank triple and S05 is PairHigh, so this cross-family pair is low.
- What engine should do: avoid over-linking unrelated families.

## Pair S01.zip,S06.zip
- Pair: `S01.zip,S06.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S06 is template-heavy while S01 is not, and post-exclusion overlap is intentionally low.
- What engine should do: keep low similarity between non-template and template-heavy families after exclusion.

## Pair S01.zip,S07.zip
- Pair: `S01.zip,S07.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S07 is template-heavy while S01 is non-template, so this pair is low after exclusion.
- What engine should do: suppress template-driven false positives across families.

## Pair S01.zip,S08.zip
- Pair: `S01.zip,S08.zip`
- Testing: `false_positive_control`
- Why expected label: S08 is a distinct control program unrelated to S01 family logic, so this pair is low.
- What engine should do: keep unrelated control comparisons low.

## Pair S01.zip,S09.zip
- Pair: `S01.zip,S09.zip`
- Testing: `false_positive_control`
- Why expected label: S09 is distinct control code and intentionally unrelated to S01, so this pair is low.
- What engine should do: avoid high scores from superficial structure overlap.

## Pair S01.zip,S10.zip
- Pair: `S01.zip,S10.zip`
- Testing: `false_positive_control`
- Why expected label: S10 is distinct control code unrelated to the S01 family, so this pair is low.
- What engine should do: keep control-vs-family comparisons low.

## Pair S02.zip,S03.zip
- Pair: `S02.zip,S03.zip`
- Testing: `cluster_consistency`
- Why expected label: both are Rank triple members with reordered methods, so this pair is high.
- What engine should do: maintain high similarity for cluster variants.

## Pair S02.zip,S04.zip
- Pair: `S02.zip,S04.zip`
- Testing: `family_separation`
- Why expected label: S02 (Rank triple) and S04 (PairHigh) are different intent groups, so this pair is low.
- What engine should do: preserve separation between distinct fixture families.

## Pair S02.zip,S05.zip
- Pair: `S02.zip,S05.zip`
- Testing: `family_separation`
- Why expected label: S02 is Rank triple while S05 is PairHigh, so this cross-family pair is low.
- What engine should do: keep unrelated families from clustering.

## Pair S02.zip,S06.zip
- Pair: `S02.zip,S06.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S06 is template-heavy and S02 is non-template, so overlap remains low after exclusion.
- What engine should do: avoid template-related false positives against non-template submissions.

## Pair S02.zip,S07.zip
- Pair: `S02.zip,S07.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S07 template-heavy code is intentionally unrelated to S02 after exclusion, so this pair is low.
- What engine should do: keep cross-family scores low when template-heavy code is present.

## Pair S02.zip,S08.zip
- Pair: `S02.zip,S08.zip`
- Testing: `false_positive_control`
- Why expected label: S08 is a distinct control program and should remain unrelated to S02, so this pair is low.
- What engine should do: avoid scoring unrelated controls as similar.

## Pair S02.zip,S09.zip
- Pair: `S02.zip,S09.zip`
- Testing: `false_positive_control`
- Why expected label: S09 is distinct control code and intentionally unrelated to S02, so this pair is low.
- What engine should do: keep unrelated control comparisons low.

## Pair S02.zip,S10.zip
- Pair: `S02.zip,S10.zip`
- Testing: `false_positive_control`
- Why expected label: S10 is distinct control code unrelated to S02 family intent, so this pair is low.
- What engine should do: avoid false positives in control comparisons.

## Pair S03.zip,S04.zip
- Pair: `S03.zip,S04.zip`
- Testing: `family_separation`
- Why expected label: S03 (Rank triple) and S04 (PairHigh) are different families, so this pair is low.
- What engine should do: preserve family-level separation.

## Pair S03.zip,S05.zip
- Pair: `S03.zip,S05.zip`
- Testing: `family_separation`
- Why expected label: S03 and S05 are intentionally in separate intent groups, so this pair is low.
- What engine should do: keep cross-family overlap low.

## Pair S03.zip,S06.zip
- Pair: `S03.zip,S06.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S06 is template-heavy and unrelated to S03 after exclusion, so this pair is low.
- What engine should do: avoid linking non-template cluster code with template-heavy variants.

## Pair S03.zip,S07.zip
- Pair: `S03.zip,S07.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S07 template-heavy logic remains unrelated to S03 post-exclusion, so this pair is low.
- What engine should do: maintain low similarity for this cross-type comparison.

## Pair S03.zip,S08.zip
- Pair: `S03.zip,S08.zip`
- Testing: `false_positive_control`
- Why expected label: S08 is a distinct control program and unrelated to S03, so this pair is low.
- What engine should do: keep control comparisons low.

## Pair S03.zip,S09.zip
- Pair: `S03.zip,S09.zip`
- Testing: `false_positive_control`
- Why expected label: S09 is distinct control logic and intentionally unrelated to S03, so this pair is low.
- What engine should do: avoid accidental high similarity from shared scaffolding.

## Pair S03.zip,S10.zip
- Pair: `S03.zip,S10.zip`
- Testing: `false_positive_control`
- Why expected label: S10 is distinct control code outside the S03 family, so this pair is low.
- What engine should do: keep unrelated submissions separated.

## Pair S04.zip,S05.zip
- Pair: `S04.zip,S05.zip`
- Testing: `pair_anchor_high`
- Why expected label: S04 and S05 are intentionally constructed as the strong high-similarity anchor pair, so this pair is high.
- What engine should do: reliably surface this known high pair.

## Pair S04.zip,S06.zip
- Pair: `S04.zip,S06.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S04 is PairHigh while S06 is template-heavy and unrelated after exclusion, so this pair is low.
- What engine should do: keep low scores for non-template vs template-heavy unrelated families.

## Pair S04.zip,S07.zip
- Pair: `S04.zip,S07.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S04 PairHigh logic and S07 template-heavy logic are unrelated post-exclusion, so this pair is low.
- What engine should do: suppress template-induced overlap across unrelated families.

## Pair S04.zip,S08.zip
- Pair: `S04.zip,S08.zip`
- Testing: `false_positive_control`
- Why expected label: S08 is distinct control code and unrelated to S04, so this pair is low.
- What engine should do: avoid high similarity for unrelated control comparisons.

## Pair S04.zip,S09.zip
- Pair: `S04.zip,S09.zip`
- Testing: `false_positive_control`
- Why expected label: S09 is distinct control logic and intentionally unrelated to S04, so this pair is low.
- What engine should do: keep unrelated pair-vs-control comparisons low.

## Pair S04.zip,S10.zip
- Pair: `S04.zip,S10.zip`
- Testing: `false_positive_control`
- Why expected label: S10 is distinct control code outside the PairHigh family, so this pair is low.
- What engine should do: avoid false positives for control submissions.

## Pair S05.zip,S06.zip
- Pair: `S05.zip,S06.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S05 PairHigh and S06 template-heavy submissions are unrelated after exclusion, so this pair is low.
- What engine should do: preserve low similarity across these different intent types.

## Pair S05.zip,S07.zip
- Pair: `S05.zip,S07.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S05 and S07 belong to unrelated families once template is excluded, so this pair is low.
- What engine should do: avoid template-driven false positives.

## Pair S05.zip,S08.zip
- Pair: `S05.zip,S08.zip`
- Testing: `false_positive_control`
- Why expected label: S08 is distinct control code unrelated to S05, so this pair is low.
- What engine should do: keep control comparisons low.

## Pair S05.zip,S09.zip
- Pair: `S05.zip,S09.zip`
- Testing: `false_positive_control`
- Why expected label: S09 is distinct control code and intentionally unrelated to S05, so this pair is low.
- What engine should do: avoid over-scoring unrelated control pairs.

## Pair S05.zip,S10.zip
- Pair: `S05.zip,S10.zip`
- Testing: `false_positive_control`
- Why expected label: S10 is distinct control code outside the S05 family, so this pair is low.
- What engine should do: keep unrelated comparisons low.

## Pair S06.zip,S07.zip
- Pair: `S06.zip,S07.zip`
- Testing: `template_exclusion`
- Why expected label: both are template-heavy variants with different unique logic, so after template exclusion this pair is low.
- What engine should do: remove template overlap and score unique logic only.

## Pair S06.zip,S08.zip
- Pair: `S06.zip,S08.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S06 template-heavy unique logic is unrelated to S08 control logic, so this pair is low.
- What engine should do: keep low similarity after template exclusion against controls.

## Pair S06.zip,S09.zip
- Pair: `S06.zip,S09.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S06 template-heavy unique logic and S09 distinct control logic are intentionally unrelated, so this pair is low.
- What engine should do: avoid false positives between template-heavy and control families.

## Pair S06.zip,S10.zip
- Pair: `S06.zip,S10.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S06 and S10 are from unrelated intent groups after exclusion, so this pair is low.
- What engine should do: keep non-matching cross-family scores low.

## Pair S07.zip,S08.zip
- Pair: `S07.zip,S08.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S07 template-heavy unique logic is unrelated to S08 control logic, so this pair is low.
- What engine should do: maintain low similarity for this cross-type comparison.

## Pair S07.zip,S09.zip
- Pair: `S07.zip,S09.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S07 template-heavy logic and S09 distinct control logic are intentionally unrelated, so this pair is low.
- What engine should do: avoid template-induced false positives against controls.

## Pair S07.zip,S10.zip
- Pair: `S07.zip,S10.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: S07 and S10 are unrelated after template exclusion, so this pair is low.
- What engine should do: keep low similarity for unrelated template-vs-control pairs.

## Pair S08.zip,S09.zip
- Pair: `S08.zip,S09.zip`
- Testing: `false_positive_control`
- Why expected label: both are distinct control programs and intentionally treated as unrelated, so this pair is low.
- What engine should do: avoid high similarity from shared scaffold/shape alone.

## Pair S08.zip,S10.zip
- Pair: `S08.zip,S10.zip`
- Testing: `false_positive_control`
- Why expected label: both are distinct control programs and intentionally treated as unrelated, so this pair is low.
- What engine should do: keep control-vs-control comparisons low.

## Pair S09.zip,S10.zip
- Pair: `S09.zip,S10.zip`
- Testing: `false_positive_control`
- Why expected label: both are in the distinct-control family and are intentionally treated as unrelated for fixture policy.
- What engine should do: avoid flagging similarity from shared scaffold/shape alone.
