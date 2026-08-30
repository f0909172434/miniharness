import { useEffect, useRef, useState } from "react";

/** 访客是否要求减少动态效果。 */
export function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(
    () => window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  );
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const onChange = () => setReduced(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

/** 元素穿过视口的进度：0 = 尚未进入，1 = 已完全越过。 */
export function useScrollProgress(ref) {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    let raf = 0;
    const measure = () => {
      raf = 0;
      const el = ref.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const vh = window.innerHeight;
      const total = rect.height + vh * 0.6;
      const passed = vh * 0.85 - rect.top;
      setProgress(Math.min(1, Math.max(0, passed / total)));
    };
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(measure);
    };
    measure();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, [ref]);
  return progress;
}

/** 元素首次进入视口时置真（一次性「通电」）。 */
export function usePowerOn(ref, threshold = 0.3) {
  const [powered, setPowered] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return undefined;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setPowered(true);
          io.disconnect();
        }
      },
      { threshold },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [ref, threshold]);
  return powered;
}

/** 本地持久化的达标集合（星图用）。 */
export function useLocalDoneSet(storageKey) {
  const [done, setDone] = useState(() => {
    try {
      return new Set(JSON.parse(localStorage.getItem(storageKey) ?? "[]"));
    } catch {
      return new Set();
    }
  });
  const toggle = (gid) => {
    setDone((prev) => {
      const next = new Set(prev);
      if (next.has(gid)) next.delete(gid);
      else next.add(gid);
      localStorage.setItem(storageKey, JSON.stringify([...next]));
      return next;
    });
  };
  return [done, toggle];
}
