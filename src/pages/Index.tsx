import { useState, useEffect } from 'react';
import Icon from '@/components/ui/icon';

const BACKEND_URL = 'https://functions.poehali.dev/16eae91a-3b2d-4e0a-a595-ccdde9b9f6f4';

const HERO_IMAGE = 'https://cdn.poehali.dev/projects/06b7a9fd-10b9-430e-85b5-30c884816cd9/files/f48041e0-a12f-4e48-bd43-c83ccb2bbd63.jpg';

const RULES = [
  { icon: 'ShieldCheck', title: 'Без гриферства', text: 'Разрушение чужих построек, воровство и вандализм строго запрещены.' },
  { icon: 'MessageSquare', title: 'Уважение в чате', text: 'Флуд, оскорбления, спам и рекламу других серверов запрещены.' },
  { icon: 'Zap', title: 'Без читов', text: 'Использование любых модов, дающих преимущество, ведёт к бану.' },
  { icon: 'Home', title: 'Свои территории', text: 'Стройте только на своей земле. Чужую территорию не занимать.' },
  { icon: 'Users', title: 'Только по заявке', text: 'Вход на сервер — только после одобрения заявки администратором.' },
  { icon: 'Crown', title: 'Слово админа — закон', text: 'Решения администрации окончательны и обязательны для всех.' },
];

const SERVER_INFO = [
  { label: 'Версия', value: 'Java 1.21.1', icon: 'Layers' },
  { label: 'Режим', value: 'Выживание', icon: 'Sword' },
  { label: 'Сложность', value: 'Hard', icon: 'Flame' },
  { label: 'Слоты', value: '50 игроков', icon: 'Users' },
  { label: 'Карта', value: '50 000 × 50 000', icon: 'Map' },
  { label: 'Тип', value: 'Приватный', icon: 'Lock' },
];

export default function Index() {
  const [telegram, setTelegram] = useState('');
  const [nick, setNick] = useState('');
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const [activeSection, setActiveSection] = useState('home');

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActiveSection(entry.target.id);
        });
      },
      { threshold: 0.4 }
    );
    ['home', 'apply', 'rules', 'contacts'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!telegram.trim() || !nick.trim() || !email.trim()) {
      setErrorMsg('Заполни все поля');
      setStatus('error');
      return;
    }
    setStatus('loading');
    setErrorMsg('');
    try {
      const res = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram: telegram.trim(), minecraft_nick: nick.trim(), email: email.trim() }),
      });
      if (res.ok) {
        setStatus('success');
        setTelegram('');
        setNick('');
        setEmail('');
      } else {
        const data = await res.json();
        setErrorMsg(data.error || 'Ошибка сервера');
        setStatus('error');
      }
    } catch {
      setErrorMsg('Нет соединения с сервером');
      setStatus('error');
    }
  };

  const navItems = [
    { id: 'home', label: 'Главная' },
    { id: 'apply', label: 'Заявка' },
    { id: 'rules', label: 'Правила' },
    { id: 'contacts', label: 'Контакты' },
  ];

  return (
    <div className="min-h-screen font-montserrat">

      {/* NAV */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-primary/20">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <button onClick={() => scrollTo('home')} className="flex items-center gap-2">
            <span className="text-2xl">⛏️</span>
            <span className="font-black text-lg tracking-wider text-primary text-glow">
              СПИ<span className="text-accent">РИТ</span>
            </span>
          </button>
          <div className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => scrollTo(item.id)}
                className={`nav-link text-sm font-semibold tracking-widest uppercase transition-colors ${
                  activeSection === item.id ? 'text-primary text-glow' : 'text-foreground/60 hover:text-foreground'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
          <button
            onClick={() => scrollTo('apply')}
            className="px-5 py-2 bg-primary text-primary-foreground font-bold text-sm tracking-wider uppercase rounded pixel-border hover:bg-primary/80 transition-all hover:scale-105"
          >
            Подать заявку
          </button>
        </div>
      </nav>

      {/* HERO */}
      <section id="home" className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{ backgroundImage: `url(${HERO_IMAGE})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/60 to-background" />
        <div className="absolute inset-0 pixel-grid opacity-30" />

        <div className="absolute top-32 left-16 w-8 h-8 bg-primary/30 pixel-border animate-float" style={{ animationDelay: '0s' }} />
        <div className="absolute top-48 right-24 w-6 h-6 bg-accent/40 pixel-border animate-float" style={{ animationDelay: '1.5s' }} />
        <div className="absolute bottom-48 left-32 w-10 h-10 bg-primary/20 pixel-border animate-float" style={{ animationDelay: '3s' }} />
        <div className="absolute bottom-32 right-16 w-7 h-7 bg-accent/30 pixel-border animate-float" style={{ animationDelay: '0.8s' }} />

        <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 glass-card rounded-full text-xs font-mono-tech text-accent tracking-widest mb-8 animate-fade-in-up">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            СЕРВЕР ОНЛАЙН — ПРИНИМАЕМ ЗАЯВКИ
          </div>

          <h1 className="text-5xl md:text-7xl font-black text-foreground leading-none mb-6 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            <span className="block text-glow text-primary">ПРИВАТНЫЙ</span>
            <span className="block">СЕРВЕР</span>
            <span className="block text-accent text-glow-cyan">СПИРИТ</span>
          </h1>

          <p className="text-foreground/60 text-lg md:text-xl max-w-xl mx-auto mb-10 animate-fade-in-up font-semibold" style={{ animationDelay: '0.2s' }}>
            Закрытое сообщество для настоящих выживальщиков.<br />
            Вступление — только по заявке.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            <button
              onClick={() => scrollTo('apply')}
              className="px-8 py-4 bg-primary text-primary-foreground font-black text-base tracking-widest uppercase pixel-border-glow rounded hover:bg-primary/80 transition-all hover:scale-105 animate-pulse-glow"
            >
              ⛏️ Подать заявку
            </button>
            <button
              onClick={() => scrollTo('rules')}
              className="px-8 py-4 glass-card text-foreground font-bold text-base tracking-widest uppercase rounded hover:border-primary/50 transition-all hover:scale-105"
            >
              📜 Правила сервера
            </button>
          </div>
        </div>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <Icon name="ChevronDown" size={24} className="text-primary/50" />
        </div>
      </section>

      {/* SERVER INFO */}
      <section className="py-20 px-6 relative">
        <div className="absolute inset-0 pixel-grid opacity-20" />
        <div className="max-w-6xl mx-auto relative">
          <div className="text-center mb-12">
            <p className="text-accent font-mono-tech tracking-widest text-sm mb-2">ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ</p>
            <h2 className="text-3xl md:text-4xl font-black text-foreground">О СЕРВЕРЕ</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {SERVER_INFO.map((item) => (
              <div key={item.label} className="glass-card rounded-lg p-5 flex items-center gap-4 hover:border-primary/40 transition-all group">
                <div className="w-10 h-10 bg-primary/10 rounded flex-shrink-0 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                  <Icon name={item.icon} fallback="Circle" size={20} className="text-primary" />
                </div>
                <div>
                  <p className="text-foreground/40 text-xs font-mono-tech tracking-wider">{item.label}</p>
                  <p className="text-foreground font-bold text-sm">{item.value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* APPLY FORM */}
      <section id="apply" className="py-24 px-6 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent" />
        <div className="max-w-lg mx-auto relative">
          <div className="text-center mb-10">
            <p className="text-accent font-mono-tech tracking-widest text-sm mb-2">ВСТУПЛЕНИЕ НА СЕРВЕР</p>
            <h2 className="text-3xl md:text-4xl font-black text-foreground mb-3">ПОДАТЬ ЗАЯВКУ</h2>
            <p className="text-foreground/50 text-sm">Заполни форму — мы рассмотрим и свяжемся с тобой в Telegram</p>
          </div>

          <div className="glass-card rounded-xl p-8 pixel-border">
            {status === 'success' ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4 pixel-border-glow">
                  <Icon name="Check" size={32} className="text-green-400" />
                </div>
                <h3 className="text-xl font-black text-foreground mb-2">Заявка отправлена!</h3>
                <p className="text-foreground/50 text-sm mb-6">Администратор рассмотрит заявку и напишет в Telegram</p>
                <button
                  onClick={() => setStatus('idle')}
                  className="px-6 py-2 glass-card text-foreground/60 hover:text-foreground text-sm font-semibold rounded transition-colors"
                >
                  Отправить ещё одну
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-xs font-mono-tech tracking-widest text-foreground/50 mb-2 uppercase">
                    Telegram username
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-primary/60 font-mono-tech">@</span>
                    <input
                      type="text"
                      value={telegram}
                      onChange={(e) => setTelegram(e.target.value)}
                      placeholder="username"
                      className="w-full bg-background/60 border border-border rounded pl-8 pr-4 py-3 text-foreground placeholder-foreground/25 font-mono-tech focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-mono-tech tracking-widest text-foreground/50 mb-2 uppercase">
                    Ник в Minecraft
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2">
                      <Icon name="Gamepad2" size={16} className="text-primary/60" />
                    </span>
                    <input
                      type="text"
                      value={nick}
                      onChange={(e) => setNick(e.target.value)}
                      placeholder="Steve"
                      className="w-full bg-background/60 border border-border rounded pl-10 pr-4 py-3 text-foreground placeholder-foreground/25 font-mono-tech focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-mono-tech tracking-widest text-foreground/50 mb-2 uppercase">
                    Ваша почта
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2">
                      <Icon name="Mail" size={16} className="text-primary/60" />
                    </span>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="example@gmail.com"
                      className="w-full bg-background/60 border border-border rounded pl-10 pr-4 py-3 text-foreground placeholder-foreground/25 font-mono-tech focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all"
                    />
                  </div>
                </div>

                {status === 'error' && (
                  <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded p-3">
                    <Icon name="AlertCircle" size={16} />
                    {errorMsg}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={status === 'loading'}
                  className="w-full py-4 bg-primary text-primary-foreground font-black text-base tracking-widest uppercase rounded pixel-border hover:bg-primary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-[1.02]"
                >
                  {status === 'loading' ? (
                    <span className="flex items-center justify-center gap-2">
                      <Icon name="Loader2" size={18} className="animate-spin" />
                      Отправка...
                    </span>
                  ) : (
                    '⛏️ Отправить заявку'
                  )}
                </button>

                <p className="text-center text-xs text-foreground/30 font-mono-tech">
                  Заявки рассматриваются в течение 24 часов
                </p>
              </form>
            )}
          </div>
        </div>
      </section>

      {/* RULES */}
      <section id="rules" className="py-24 px-6 relative">
        <div className="absolute inset-0 pixel-grid opacity-15" />
        <div className="max-w-6xl mx-auto relative">
          <div className="text-center mb-12">
            <p className="text-accent font-mono-tech tracking-widest text-sm mb-2">ОБЯЗАТЕЛЬНО К ПРОЧТЕНИЮ</p>
            <h2 className="text-3xl md:text-4xl font-black text-foreground mb-3">ПРАВИЛА СЕРВЕРА</h2>
            <p className="text-foreground/40 text-sm">Нарушение правил = бан без предупреждения</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {RULES.map((rule, i) => (
              <div
                key={rule.title}
                className="glass-card rounded-xl p-6 hover:border-primary/40 transition-all group hover:scale-[1.02]"
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded flex-shrink-0 flex items-center justify-center group-hover:bg-primary/20 transition-colors pixel-border">
                    <Icon name={rule.icon} fallback="Circle" size={18} className="text-primary" />
                  </div>
                  <div>
                    <h3 className="font-black text-foreground mb-1 tracking-wide">{rule.title}</h3>
                    <p className="text-foreground/50 text-sm leading-relaxed">{rule.text}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-10 glass-card rounded-xl p-6 border-accent/30 text-center">
            <p className="text-accent font-mono-tech text-sm tracking-wider">
              📋 Незнание правил не освобождает от ответственности
            </p>
          </div>
        </div>
      </section>

      {/* CONTACTS */}
      <section id="contacts" className="py-24 px-6 relative">
        <div className="absolute inset-0 bg-gradient-to-t from-primary/5 to-transparent" />
        <div className="max-w-3xl mx-auto relative">
          <div className="text-center mb-12">
            <p className="text-accent font-mono-tech tracking-widest text-sm mb-2">СВЯЗЬ С АДМИНИСТРАЦИЕЙ</p>
            <h2 className="text-3xl md:text-4xl font-black text-foreground">КОНТАКТЫ</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-card rounded-xl p-8 pixel-border hover:scale-[1.02] transition-all group">
              <div className="w-14 h-14 bg-primary/10 rounded-xl flex items-center justify-center mb-5 group-hover:bg-primary/20 transition-colors">
                <Icon name="Send" size={26} className="text-primary" />
              </div>
              <h3 className="font-black text-foreground text-lg mb-2 tracking-wide">Telegram</h3>
              <p className="text-foreground/40 text-sm mb-4">Главный канал связи с администратором</p>
              <div className="font-mono-tech text-primary text-sm bg-primary/10 px-3 py-2 rounded">
                @mXRlBLhQh
              </div>
            </div>

            <div className="glass-card rounded-xl p-8 hover:scale-[1.02] transition-all group">
              <div className="w-14 h-14 bg-accent/10 rounded-xl flex items-center justify-center mb-5 group-hover:bg-accent/20 transition-colors">
                <Icon name="Clock" size={26} className="text-accent" />
              </div>
              <h3 className="font-black text-foreground text-lg mb-2 tracking-wide">Время ответа</h3>
              <p className="text-foreground/40 text-sm mb-4">Администратор онлайн каждый день</p>
              <div className="font-mono-tech text-accent text-sm bg-accent/10 px-3 py-2 rounded">
                18:00 — 23:00 МСК
              </div>
            </div>
          </div>

          <div className="mt-6 glass-card rounded-xl p-6 text-center">
            <p className="text-foreground/40 text-sm font-mono-tech tracking-wide">
              По вопросам заявок писать только после заполнения формы
            </p>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-border py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xl">⛏️</span>
            <span className="font-black tracking-widest text-primary">СПИ<span className="text-accent">РИТ</span></span>
            <span className="text-foreground/30 font-mono-tech text-xs ml-2">PRIVATE SERVER</span>
          </div>
          <p className="text-foreground/25 font-mono-tech text-xs tracking-wider">
            © 2024 — Только по приглашению
          </p>
          <div className="flex gap-6">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => scrollTo(item.id)}
                className="text-foreground/30 hover:text-foreground/60 text-xs font-semibold tracking-wider uppercase transition-colors"
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}