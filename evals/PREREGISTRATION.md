# Confirmation decision rule

Freeze this file, the model configuration, the confirmation briefs, and the
randomization seed before generating confirmation outputs.

The treatment passes only when every condition holds:

1. pooled treatment-minus-control **decision fit** is at least `0.00`, and no
   brief has a median difference below `-1.0`;
2. pooled treatment-minus-control **causal clarity** is at least `+0.30`;
3. pooled treatment-minus-control **robustness** is at least `+0.40`;
4. pooled treatment-minus-control **actionability** is at least `0.00`;
5. collapse repeated runs to one majority WANT decision per brief × judge;
   after tied cells are removed, treatment wins more than 50% and the lower
   bound of its two-sided 95% Wilson interval is above `0.50`;
6. treatment mean total tokens are at most `2.0x` control and wall time is at
   most `3.0x` control;
7. every preregistered brief has every planned run and judge.

All conditions are conjunctive. A development win or a favourable unregistered
metric is not a pass. If the rule fails, implicit invocation stays disabled.

This evaluation asks whether the workshop improves a selected direction. It
does not test whether the direction should have been generated or selected in
the first place.
