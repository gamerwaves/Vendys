document.addEventListener("DOMContentLoaded", function () {
  const dollarInput = document.getElementById("calc_dollars");
  const userTypeRadios = document.querySelectorAll("input[name='calc_user_type']");
  const resultBox = document.getElementById("points_result");

  const pointInput = document.getElementById("calc_points");
  const revUserRadios = document.querySelectorAll("input[name='rev_user_type']");
  const dollarResultBox = document.getElementById("dollar_result");

  function updatePoints() {
    const dollars = parseFloat(dollarInput.value);
    const userType = document.querySelector("input[name='calc_user_type']:checked").value;

    if (!dollars || dollars < 1) {
      resultBox.style.display = "none";
      return;
    }

    fetch("/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dollars: dollars,
        premium: userType === "p"
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.points !== undefined) {
        resultBox.textContent = `Estimated Points: ${data.points}`;
        resultBox.style.display = "block";
      } else {
        resultBox.textContent = "Error calculating points.";
        resultBox.style.display = "block";
      }
    })
    .catch(() => {
      resultBox.textContent = "Error calculating points.";
      resultBox.style.display = "block";
    });
  }

  function reverseCalculateDollars() {
    const targetPoints = parseFloat(pointInput.value);
    const isPremium = document.querySelector("input[name='rev_user_type']:checked").value === "p";

    if (!targetPoints || targetPoints < 1) {
      dollarResultBox.style.display = "none";
      return;
    }

    const baseRate = isPremium ? 3 : 5;
    const bonusMult = isPremium ? 1 : 2;

    // Binary search to reverse calculate the dollars
    let low = 0.01, high = 10000, mid, result = null;

    function estimatePoints(dollars) {
      return baseRate * dollars + Math.log2(dollars) * bonusMult;
    }

    for (let i = 0; i < 30; i++) {
      mid = (low + high) / 2;
      const est = estimatePoints(mid);

      if (Math.abs(est - targetPoints) < 0.01) {
        result = mid;
        break;
      }

      if (est < targetPoints) {
        low = mid;
      } else {
        high = mid;
        result = mid;
      }
    }

    if (result) {
      dollarResultBox.textContent = `Approximate Dollar Amount: $${result.toFixed(2)}`;
    } else {
      dollarResultBox.textContent = "Could not approximate.";
    }

    dollarResultBox.style.display = "block";
  }

  dollarInput.addEventListener("input", updatePoints);
  userTypeRadios.forEach(r => r.addEventListener("change", updatePoints));

  pointInput.addEventListener("input", reverseCalculateDollars);
  revUserRadios.forEach(r => r.addEventListener("change", reverseCalculateDollars));
});

document.getElementById("modeSelect").addEventListener("change", function () {
  const mode = this.value;
  document.getElementById("calc-form").style.display = mode === "dollarsToPoints" ? "block" : "none";
  document.getElementById("reverse-calc-form").style.display = mode === "pointsToDollars" ? "block" : "none";
});