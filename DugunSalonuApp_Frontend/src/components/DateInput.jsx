import { useCallback, useEffect, useRef, useState } from "react";
import { formatInputDate, isIsoDate, normalizeToIsoDate } from "../api/date";

export default function DateInput({ value, onChange, name, required, allowEmpty = false }) {
  const [displayValue, setDisplayValue] = useState(() => formatInputDate(value));
  const nativeRef = useRef(null);

  useEffect(() => {
    setDisplayValue(formatInputDate(value));
  }, [value]);

  const handleDisplayChange = useCallback(
    (event) => {
      const nextValue = event.target.value;
      setDisplayValue(nextValue);
      const isoValue = normalizeToIsoDate(nextValue);
      if (isIsoDate(isoValue)) {
        onChange?.(isoValue);
      }
    },
    [onChange],
  );

  const handleDisplayBlur = useCallback(() => {
    const isoValue = normalizeToIsoDate(displayValue);
    if (!displayValue.trim()) {
      if (allowEmpty) {
        onChange?.("");
        setDisplayValue("");
        return;
      }
      setDisplayValue(formatInputDate(value));
      return;
    }
    if (isIsoDate(isoValue)) {
      onChange?.(isoValue);
      setDisplayValue(formatInputDate(isoValue));
      return;
    }
    setDisplayValue(formatInputDate(value));
  }, [allowEmpty, displayValue, onChange, value]);

  const handleOpenPicker = useCallback(() => {
    const input = nativeRef.current;
    if (!input) {
      return;
    }
    if (typeof input.showPicker === "function") {
      input.showPicker();
    } else {
      input.focus();
      input.click();
    }
  }, []);

  const handleNativeChange = useCallback(
    (event) => {
      const isoValue = event.target.value;
      if (!isIsoDate(isoValue)) {
        return;
      }
      onChange?.(isoValue);
      setDisplayValue(formatInputDate(isoValue));
    },
    [onChange],
  );

  return (
    <div className="date-input-wrapper">
      <input
        name={name}
        type="text"
        className="date-input"
        inputMode="numeric"
        placeholder="DD/MM/YYYY"
        value={displayValue}
        onChange={handleDisplayChange}
        onBlur={handleDisplayBlur}
        onClick={handleOpenPicker}
        readOnly
        aria-readonly="true"
        required={required}
        autoComplete="off"
      />
      <input
        ref={nativeRef}
        type="date"
        className="date-input-native"
        value={isIsoDate(value) ? value : ""}
        onChange={handleNativeChange}
        tabIndex={-1}
        aria-hidden="true"
      />
    </div>
  );
}
