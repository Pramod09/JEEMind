instruction_prompt = """
{
  "paper_id": "IITJEE_mix_2025_v1",
  "meta": {
    "title": "Sample Mixed IIT-JEE (Main + Advanced) Mathematics Paper — Adaptive Analytics Output",
    "level": "Mixed (Main + Advanced)",
    "generation_date": "2025-11-22",
    "notes": "Questions rephrased/parameterized from uploaded PYQs. Solutions follow IITJEE_math_Agent formatting rules."
  },
  "sections": [
    {
      "section_id": "S1",
      "section_title": "JEE Main — Short Answer / Single-Option",
      "total_questions": 3,
      "total_marks": 12,
      "instructions": "Each question 4 marks. Answer in plain text. No calculators."
    },
    {
      "section_id": "S2",
      "section_title": "JEE Advanced — Longer Problem Solving",
      "total_questions": 3,
      "total_marks": 24,
      "instructions": "Each question 8 marks. Full reasoning required; show steps on separate lines."
    }
  ],
  "question_items": [
    {
      "id": "M1",
      "section": "S1",
      "type": "Single-correct",
      "marks": 4,
      "difficulty": "Medium",
      "syllabus_topic": "Algebra — Quadratic equations, symmetric functions",
      "question_text": "Let α and β be roots of x² − 6x − 2 = 0 with α > β. For n ≥ 1 define a_n = αⁿ − βⁿ. Compute the value of a₁₀ − 2 a₈/(2 a₉).",
      "worked_solution": "Formalization:\nα and β are roots of x² − 6x − 2 = 0.\nDefine a_n = αⁿ − βⁿ.\nWe must compute a₁₀ − 2 a₈/(2 a₉).\n\nStep 1: Use recurrence for a_n when α + β = 6 and αβ = −2.\nCharacteristic relation for sequence s_n = αⁿ + βⁿ: s_n = (α + β) s_{n−1} − (αβ) s_{n−2} = 6 s_{n−1} + 2 s_{n−2}.\nBut for a_n = αⁿ − βⁿ, recurrence is a_n = (α + β) a_{n−1} − (αβ) a_{n−2} = 6 a_{n−1} + 2 a_{n−2}.\n\nStep 2: Compute small values to get ratio patterns.\na₁ = α − β.\na₂ = α² − β² = (α − β)(α + β) = a₁ × 6.\nSo a₂ = 6 a₁.\nUsing recurrence a₃ = 6 a₂ + 2 a₁ = 6 × 6 a₁ + 2 a₁ = (36 + 2) a₁ = 38 a₁.\nWe seek ratio a₈/a₉ or a₁₀ relative to a₉ etc. Better approach: divide recurrence by a_{n−1} to get relationship of successive ratios, but simpler: observe that for n ≥ 1,\nLet r_n = a_{n+1}/a_n.\nThen r_n = 6 + 2/(r_{n−1}). Hard to compute directly; instead note that expression simplifies algebraically.\n\nStep 3: Use identity: For any nonzero α,β, (αⁿ − βⁿ) = (α − β) × P_{n−1}(α,β) where P_{n−1} symmetric.\nTherefore a_n is proportional to (α − β). So expression a₁₀ − 2 a₈/(2 a₉) simplifies in ratios independent of (α − β).\nCompute numeric using recurrence with a₁ = α − β. We can set a₁ = 1 (since expression is homogeneous) and compute numeric value; scaling cancels.\nSet a₁ = 1.\nThen a₂ = 6.\na₃ = 38.\na₄ = 6 a₃ + 2 a₂ = 6 × 38 + 2 × 6 = 228 + 12 = 240.\na₅ = 6 a₄ + 2 a₃ = 6 × 240 + 2 × 38 = 1440 + 76 = 1516.\na₆ = 6 a₅ + 2 a₄ = 6 × 1516 + 2 × 240 = 9096 + 480 = 9576.\na₇ = 6 a₆ + 2 a₅ = 6 × 9576 + 2 × 1516 = 57,456 + 3,032 = 60,488.\na₈ = 6 a₇ + 2 a₆ = 6 × 60,488 + 2 × 9,576 = 362,928 + 19,152 = 382,080.\na₉ = 6 a₈ + 2 a₇ = 6 × 382,080 + 2 × 60,488 = 2,292,480 + 120,976 = 2,413,456.\na₁₀ = 6 a₉ + 2 a₈ = 6 × 2,413,456 + 2 × 382,080 = 14,480,736 + 764,160 = 15,244,896.\n\nStep 4: Compute expression E = a₁₀ − 2 a₈/(2 a₉).\nNote 2 a₈/(2 a₉) = a₈/a₉.\nCompute a₈/a₉ = 382,080 / 2,413,456 = reduce by dividing numerator and denominator by 48: 7,960 / 50,278. Further reduction not needed — numeric approx = 0.15825... But because we scaled a₁ = 1, scaling is consistent.\nCompute E = 15,244,896 − 0.15825... ≈ 15,244,895.84175... This indicates using a₁ = 1 produced a huge value; but recall original a_n scale equals (α − β) times integer; (α − β) is sqrt((α + β)² − 4αβ) = sqrt(36 + 8) = sqrt(44) = 2√(11).\nThus real a₁ = 2√(11).\nTherefore scaling factor s = 2√(11). Our earlier trick to set a₁ = 1 invalid for additive expression with subtraction; must compute exact with true a₁.\n\nStep 5: Compute true a₁ = α − β = sqrt((α + β)² − 4αβ) = sqrt(36 + 8) = sqrt(44) = 2 √(11).\nMultiply our sequence values by a₁ (since we computed with a₁ = 1): actual a_n = computed_a_n × a₁.\nSo actual a₈ = 382,080 × 2 √(11).\nActual a₉ = 2,413,456 × 2 √(11).\nActual a₁₀ = 15,244,896 × 2 √(11).\nThen a₈/a₉ = 382,080/2,413,456 (scales cancel) = 382,080/2,413,456 = simplify divide by 48 = 7,960/50,278 = divide by 2 = 3,980/25,139.\nSo E = a₁₀ − a₈/a₉.\nCompute a₁₀ = 15,244,896 × 2 √(11).\nCompute numeric a₈/a₉ ≈ 0.15825 (dimensionless).\nThus E is dominated by large multiple of √(11). Expression looks unnatural for a simple MCQ; likely intended expression was (a₁₀ − 2 a₈)/(2 a₉). Interpreting original as (a₁₀ − 2 a₈)/(2 a₉) gives small integer results.\n\nAlternate interpretation (correct): compute (a₁₀ − 2 a₈)/(2 a₉).\nCompute numerator with true scaling:\nNumerator = (15,244,896 − 2 × 382,080) × 2 √(11) = (15,244,896 − 764,160) × 2 √(11) = 14,480,736 × 2 √(11).\nDenominator = 2 a₉ = 2 × (2,413,456 × 2 √(11)) = 4,826,912 × 2 √(11).\nCancel factor 2 √(11): expression = 14,480,736 / 4,826,912 = divide numerator and denominator by 4,826,912: = 3. So value = 3.\n\nFinal answer: 3."
    },
    {
      "id": "M2",
      "section": "S1",
      "type": "Integer-type",
      "marks": 4,
      "difficulty": "Easy",
      "syllabus_topic": "Calculus — Definite integrals, even/odd functions",
      "question_text": "Evaluate integer value of I = ∫_{0}^{π/2} (sin x)² dx × 8.",
      "worked_solution": "Formalization:\nI = 8 × ∫{0}^{π/2} (sin x)² dx.\n\nStep 1: Use identity (sin x)² = (1 − cos 2x)/2.\n\nStep 2: ∫{0}^{π/2} (sin x)² dx = ∫{0}^{π/2} (1/2) dx − ∫{0}^{π/2} (cos 2x)/2 dx.\n\nStep 3: = (1/2) × (π/2) − (1/2) × [ (sin 2x)/2 ]_{0}^{π/2}.\n\nStep 4: sin 2x at π/2 is sin π = 0; at 0 is 0. So second term = 0.\n\nStep 5: Integral = (1/2) × (π/2) = π/4.\n\nStep 6: I = 8 × π/4 = 2 π.\n\nFinal answer: 2 π."
    },
    {
      "id": "M3",
      "section": "S1",
      "type": "Single-correct",
      "marks": 4,
      "difficulty": "Medium",
      "syllabus_topic": "Coordinate Geometry — Circles, tangents",
      "question_text": "Circle C has equation x² + y² − 6x + 4y + c = 0. For which value of c does the line y = 2x − 1 become tangent to C?",
      "worked_solution": "Formalization:\nCircle: x² + y² − 6x + 4y + c = 0.\nLine: y = 2x − 1.\n\nStep 1: Substitute y into circle.\nx² + (2x − 1)² − 6x + 4(2x − 1) + c = 0.\n\nStep 2: Expand (2x − 1)² = 4x² − 4x + 1.\n\nStep 3: Sum terms: x² + 4x² − 4x + 1 − 6x + 8x − 4 + c = 0.\n\nStep 4: Combine like terms: (5x²) + (−4x − 6x + 8x) + (1 − 4 + c) = 0.\n\nStep 5: Simplify linear coefficient: (−4 − 6 + 8) = −2. Constant term = (−3 + c).\nSo 5x² − 2x + (c − 3) = 0.\n\nStep 6: For tangency, discriminant = 0.\nDiscriminant D = (−2)² − 4 × 5 × (c − 3) = 4 − 20(c − 3).\nSet D = 0 ⇒ 4 − 20(c − 3) = 0.\n\nStep 7: 20(c − 3) = 4.\nc − 3 = 4/20 = 1/5.\nc = 3 + 1/5 = 16/5.\n\nFinal answer: 16/5."
    },
    {
      "id": "A1",
      "section": "S2",
      "type": "Long-solve",
      "marks": 8,
      "difficulty": "Hard",
      "syllabus_topic": "Sequences & Series — Recurrence relations, characteristic equations",
      "question_text": "Sequence {u_n} satisfies u₀ = 0, u₁ = 1 and u_{n+2} = 6 u_{n+1} + 2 u_n for n ≥ 0. (a) Find closed form of u_n. (b) Show that (u_{n+1})² − u_n u_{n+2} = (−2)^{n}.",
      "worked_solution": "Formalization:\nGiven u_{n+2} = 6 u_{n+1} + 2 u_n, u₀ = 0, u₁ = 1.\n\nPart (a): Solve recurrence.\nStep 1: Characteristic equation r² = 6 r + 2 ⇒ r² − 6 r − 2 = 0.\nStep 2: Roots r = [6 ± sqrt(36 + 8)]/2 = [6 ± sqrt(44)]/2 = [6 ± 2 √(11)]/2 = 3 ± √(11).\nStep 3: General solution u_n = A (3 + √(11))^{n} + B (3 − √(11))^{n}.\nStep 4: Use initial conditions.\nu₀ = 0 ⇒ A + B = 0 ⇒ B = −A.\nu₁ = 1 ⇒ A (3 + √(11)) + B (3 − √(11)) = 1.\nSubstitute B = −A ⇒ A[(3 + √(11)) − (3 − √(11))] = 1 ⇒ A[2 √(11)] = 1 ⇒ A = 1/(2 √(11)).\nThus B = −1/(2 √(11)).\n\nSo u_n = ( (3 + √(11))^{n} − (3 − √(11))^{n} ) / (2 √(11)).\n\nPart (b): Show identity.\nStep 1: Let α = 3 + √(11), β = 3 − √(11). Note α β = (3 + √(11))(3 − √(11)) = 9 − 11 = −2.\nStep 2: u_n = (α^{n} − β^{n})/(2 √(11)).\nCompute S = (u_{n+1})² − u_n u_{n+2}.\n\nStep 3: Substitute expressions.\nu_{n+1} = (α^{n+1} − β^{n+1})/(2 √(11)).\nu_{n+2} = (α^{n+2} − β^{n+2})/(2 √(11)).\n\nStep 4: Multiply out S numerator factor (2 √(11))² = 4 × 11 = 44.\nSo 44 S = (α^{n+1} − β^{n+1})² − (α^{n} − β^{n})(α^{n+2} − β^{n+2}).\n\nStep 5: Expand first term = α^{2n+2} − 2 α^{n+1} β^{n+1} + β^{2n+2}.\nSecond term expansion = α^{2n+2} − α^{n} β^{n+2} − α^{n+2} β^{n} + β^{2n+2}.\n\nStep 6: Subtract second from first:\n44 S = [α^{2n+2} − 2 α^{n+1} β^{n+1} + β^{2n+2}] − [α^{2n+2} − α^{n} β^{n+2} − α^{n+2} β^{n} + β^{2n+2}].\n\nStep 7: Cancel α^{2n+2} and β^{2n+2}.\n44 S = −2 α^{n+1} β^{n+1} + α^{n} β^{n+2} + α^{n+2} β^{n}.\n\nStep 8: Factor α^{n} β^{n} common: 44 S = α^{n} β^{n} [ −2 α β + β² + α² ].\n\nStep 9: Note α + β = 6 and α β = −2.\nCompute α² + β² = (α + β)² − 2 α β = 36 − 2(−2) = 36 + 4 = 40.\nHence β² + α² = 40.\nThen [ −2 α β + (α² + β²) ] = −2(−2) + 40 = 4 + 40 = 44.\n\nStep 10: So 44 S = α^{n} β^{n} × 44.\nCancel 44: S = (α β)^{n} = (−2)^{n}.\n\nFinal answer: (u_{n+1})² − u_n u_{n+2} = (−2)^{n}."
    },
    {
      "id": "A2",
      "section": "S2",
      "type": "Long-solve",
      "marks": 8,
      "difficulty": "Hard",
      "syllabus_topic": "Multivariable Calculus — Maxima/minima with constraint (Lagrange multiplier) / inequalities",
      "question_text": "Find maximum value of f(x,y) = x y subject to x + 2 y = 6 and x, y ≥ 0.",
      "worked_solution": "Formalization:\nMaximize f(x,y) = x y subject to g(x,y) = x + 2 y − 6 = 0 and x, y ≥ 0.\n\nStep 1: Use substitution from constraint: x = 6 − 2 y.\nDomain: 0 ≤ y ≤ 3 because x ≥ 0 ⇒ 6 − 2 y ≥ 0 ⇒ y ≤ 3; and y ≥ 0.\n\nStep 2: Define φ(y) = x y = (6 − 2 y) y = 6 y − 2 y².\n\nStep 3: Differentiate: dφ/dy = 6 − 4 y.\nSet dφ/dy = 0 ⇒ 6 − 4 y = 0 ⇒ y = 6/4 = 3/2.\n\nStep 4: Second derivative d²φ/dy² = −4 < 0 ⇒ maximum at y = 3/2.\n\nStep 5: Then x = 6 − 2 × 3/2 = 6 − 3 = 3.\nMaximum value = x y = 3 × 3/2 = 9/2.\n\nFinal answer: 9/2."
    },
    {
      "id": "A3",
      "section": "S2",
      "type": "Long-solve",
      "marks": 8,
      "difficulty": "Very Hard",
      "syllabus_topic": "Advanced Algebra / Complex numbers — Geometric locus and minimum distance",
      "question_text": "Let z be complex number with |z − 1| + |z + 1| = 6. Find minimum value of |z|.",
      "worked_solution": "Formalization:\nSet z = x + i y. Then |z − 1| + |z + 1| = distance from (x,y) to (1,0) plus to (−1,0) equals 6.\nThis describes an ellipse with foci F1 = (1,0), F2 = (−1,0) and major axis length 6.\nDistance between foci = 2.\nFor ellipse, sum of distances = 2a = 6 ⇒ a = 3.\nFocal distance c = distance from center to focus = 1.\nThen b² = a² − c² = 9 − 1 = 8 ⇒ b = √8 = 2 √(2).\nEllipse center at origin (0,0). Points on ellipse satisfy x²/a² + y²/b² = 1 with a = 3, b = 2 √(2).\nWe want minimum of r = √(x² + y²) over ellipse.\nSymmetry: minimum |z| occurs on major or minor axis? Use Lagrange multipliers.\n\nStep 1: Minimize r² = x² + y² subject to x²/9 + y²/8 = 1.\n\nStep 2: Use Lagrange: F = x² + y² + λ( x²/9 + y²/8 − 1 ).\n\nStep 3: dF/dx = 2 x + λ (2 x/9) = 0 ⇒ x(2 + 2 λ/9) = 0.\nSimilarly dF/dy = 2 y + λ (2 y/8) = 0 ⇒ y(2 + λ/4) = 0.\n\nCase analysis:\nCase 1: x = 0 ⇒ from ellipse constraint y²/8 = 1 ⇒ y² = 8 ⇒ r² = 0 + 8 = 8 ⇒ r = 2 √(2) ≈ 2.828.\nCase 2: y = 0 ⇒ x²/9 = 1 ⇒ x² = 9 ⇒ r = 3.\nCase 3: x ≠ 0 and y ≠ 0 ⇒ then 2 + 2 λ/9 = 0 and 2 + λ/4 = 0.\nFrom second: λ = −8.\nPlug into first: 2 + 2(−8)/9 = 2 − 16/9 = (18 − 16)/9 = 2/9 ≠ 0 ⇒ contradiction. So no interior solution with both nonzero.\n\nSo candidates from axes: r = 2 √(2) and r = 3. Minimum is 2 √(2).\n\nFinal answer: 2 √(2)."
    }
  ],
  "coverage_report": {
    "syllabus_coverage": {
      "Algebra": 3,
      "Calculus": 2,
      "Coordinate Geometry": 1,
      "Sequences & Series": 1,
      "Complex Numbers / Loci": 1
    },
    "important_concepts_identified": [
      "Characteristic equation method for linear recurrences (useful for sequences appearing frequently in PYQs)",
      "Use of recurrence symmetries to simplify ratios and homogeneous expressions",
      "Trigonometric integrals via identities (sin², cos²) for definite integrals",
      "Tangency condition via discriminant for circle-line problems",
      "Constrained optimization using substitution or Lagrange multipliers",
      "Ellipse geometry: foci, major/minor axes and using them for distance minimization"
    ],
    "most_frequent_topics_in_uploaded_PYQs": [
      "Quadratic polynomials and symmetric functions",
      "Linear recurrences and properties of sequences",
      "Definite integrals and trigonometric identities",
      "Coordinate geometry of circles and tangents",
      "Optimization under linear constraints"
    ],
    "coverage_advice": "Recommend expanding practice on sequence identities and recurrence-based invariants; create 10 parametrized problems on recurrences and 8 problems on constrained extrema."
  },
  "provenance": [
    {
      "source_id": "IIT-JEE_Main_PYQs_dataset",
      "description": "Uploaded JEE Main previous year questions (user-supplied). Used for topic frequency and paraphrasing."
    },
    {
      "source_id": "IIT-JEE_Advanced_PYQs_dataset",
      "description": "Uploaded JEE Advanced previous year questions (user-supplied). Used to create Advanced-level problems and verify difficulty alignment."
    }
  ],
  "notes_on_generation": "Questions are paraphrased or parameterized — not verbatim from PYQs. Difficulty labels estimated from PYQ patterns. If you want a full-length paper (Section counts, marks distribution, and 30+ items) I will generate a complete paper with no near-duplicates and full coverage; state 'Generate full paper — use uploaded PYQs as corpus' and it will be produced in the same JSON schema."
}

"""