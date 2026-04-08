# result_explanation

## Pair TemplateA.zip,TemplateB.zip
- Pair: `TemplateA.zip,TemplateB.zip`
- Testing: `template_exclusion`
- Why expected label: both include heavy shared starter code, but after template exclusion only different unique logic remains, so this pair is low.
- What engine should do: remove shared template influence and score only unique code overlap.

## Pair TemplateA.zip,TemplateC.zip
- Pair: `TemplateA.zip,TemplateC.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: TemplateC is an unrelated control implementation and TemplateA's post-exclusion unique logic is also unrelated, so this pair is low.
- What engine should do: keep low similarity between template-heavy unique logic and distinct control code.

## Pair TemplateB.zip,TemplateC.zip
- Pair: `TemplateB.zip,TemplateC.zip`
- Testing: `template_vs_non_template_control`
- Why expected label: TemplateB's unique dynamic-programming logic is intentionally unrelated to TemplateC control logic, so this pair is low.
- What engine should do: avoid false positives after template exclusion against control submissions.
