/**
 * Zero-dependency pure Canvas/SVG Charting Engine for Platform KPIs
 */

const LMSCharts = {
  renderBarChart: function (canvasId, labels, data, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);
    const maxValue = Math.max(...data, 10);
    const barWidth = (width - 60) / data.length - 15;
    const chartHeight = height - 50;

    data.forEach((val, idx) => {
      const barHeight = (val / maxValue) * chartHeight;
      const x = 40 + idx * (barWidth + 15);
      const y = height - 30 - barHeight;

      // Draw bar
      ctx.fillStyle = colors[idx % colors.length] || "#3b82f6";
      ctx.beginPath();
      ctx.roundRect(x, y, barWidth, barHeight, [4, 4, 0, 0]);
      ctx.fill();

      // Draw value text
      ctx.fillStyle = "#9ca3af";
      ctx.font = "11px system-ui";
      ctx.textAlign = "center";
      ctx.fillText(val, x + barWidth / 2, y - 6);

      // Draw label
      ctx.fillText(labels[idx], x + barWidth / 2, height - 10);
    });
  },
};
