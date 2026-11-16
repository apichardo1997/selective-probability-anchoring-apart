import Mathlib

/-- Log-odds of two option scores. A normalising constant cancels in the ratio. -/
noncomputable def logOdds (pA pB : ℝ) : ℝ := Real.log (pA / pB)

/-- Remark 1: uniform anchoring scales the log-odds shift by (1 - lam). -/
theorem uniform_contraction (cA cB bA bB lam : ℝ)
    (hcA : 0 < cA) (hcB : 0 < cB) (hbA : 0 < bA) (hbB : 0 < bB) :
    logOdds (cA ^ (1 - lam) * bA ^ lam) (cB ^ (1 - lam) * bB ^ lam) - logOdds bA bB
      = (1 - lam) * (logOdds cA cB - logOdds bA bB) := by
  unfold logOdds
  have h1 : 0 < cA ^ (1 - lam) := Real.rpow_pos_of_pos hcA _
  have h2 : 0 < bA ^ lam := Real.rpow_pos_of_pos hbA _
  have h3 : 0 < cB ^ (1 - lam) := Real.rpow_pos_of_pos hcB _
  have h4 : 0 < bB ^ lam := Real.rpow_pos_of_pos hbB _
  rw [Real.log_div (mul_pos h1 h2).ne' (mul_pos h3 h4).ne',
      Real.log_mul h1.ne' h2.ne', Real.log_mul h3.ne' h4.ne',
      Real.log_rpow hcA, Real.log_rpow hbA, Real.log_rpow hcB, Real.log_rpow hbB,
      Real.log_div hcA.ne' hcB.ne', Real.log_div hbA.ne' hbB.ne']
  ring

/-- For lam < 1 the ratio of evidence shift to absolute pressure shift is unchanged. -/
theorem selectivity_ratio_unchanged (e p lam : ℝ) (h : lam < 1) :
    ((1 - lam) * e) / |(1 - lam) * p| = e / |p| := by
  have h' : 0 < 1 - lam := by linarith
  rw [abs_mul, abs_of_pos h']
  exact mul_div_mul_left e |p| h'.ne'

#print axioms uniform_contraction
#print axioms selectivity_ratio_unchanged
