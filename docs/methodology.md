# Methodology

## KPI: 12-month early attrition

`Early Attrition Rate = exits within 12 months of the hire date ÷ hires in the complete cohort`.

**Right-censoring.** Someone hired five months ago cannot yet have left "within 12 months". Counting every hire in the
denominator therefore *understates* the rate. The KPI is computed only on the **complete cohort**: hires made on or before
`obs_end − 365 days`. The report shows the naive rate next to the correct one so the bias is visible.

`kaplan_meier()` uses *all* hires (incomplete ones are censored at their observed tenure) and serves as a cross-check:
its 12-month value should sit close to the complete-cohort rate.

## Group comparison

For each dimension (team, grade, site, contract, manager change) the report shows the 12-month rate with a **Wilson 95%
interval** and a chi-square p-value for the dimension. A group is coloured only when its interval *excludes* the overall
rate. Small groups produce wide intervals; that is intentional: it keeps noise from being read as signal.

## Drivers

A logistic regression (`exited12 ~ manager_changed + onboarding_z + pay_ratio_z + overtime_z + fixed_term + grade + team + site`)
estimates each factor's effect while holding the others constant. Continuous predictors are standardised, so effects are
"per 1 SD". The report translates odds ratios into plain language (for example "×2.1 odds of leaving") and reports AUC
as a reminder that the model explains only part of the variation. Rows with a missing onboarding score are excluded from
the model only.

## Risk stacking and prioritisation

Four binary flags (pay ratio below threshold, onboarding score below threshold, overtime at or above threshold,
manager change) are counted per person and grouped into 0, 1 and 2+. **Thresholds are exploratory**: they are set in
`Config` and, if tuned on the same data, must be validated on a later cohort.

Priority uses *excess exits* = people with the factor × (rate with factor − rate without). Factors are correlated, so
these numbers are for ranking only; they are not additive and not causal.

## Limitations

- Associations, not causes. Use pilots with control groups to test interventions.
- Exit reasons are self-reported.
- The demo data is synthetic; effect sizes are chosen by the generator and carry no real-world meaning.
