export function formatHours(value) {
  const number = Number(value || 0);
  const hours = Math.floor(number);
  const minutes = Math.round((number - hours) * 60);
  if (hours === 0) {
    return `${minutes}m`;
  }
  if (minutes === 0) {
    return `${hours}h`;
  }
  return `${hours}h ${minutes}m`;
}

export function formatClock(absoluteHour) {
  const day = Math.floor(absoluteHour / 24) + 1;
  const hourInDay = absoluteHour % 24;
  const hour = Math.floor(hourInDay);
  const minute = Math.round((hourInDay - hour) * 60);
  return `Day ${day}, ${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}

export function downloadDataUrl(dataUrl, filename) {
  const link = document.createElement("a");
  link.href = dataUrl;
  link.download = filename;
  link.click();
}

