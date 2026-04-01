/**
 * Button — primary / secondary / ghost / danger variants.
 * Matches the existing #3b3660 brand purple used across instructor pages.
 */
const variants = {
  primary:   'bg-brand-purple text-white hover:bg-purple-clicked',
  secondary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
  ghost:     'text-brand-purple hover:underline bg-transparent',
  danger:    'bg-red-50 text-red-700 border border-red-200 hover:bg-red-100',
  success:   'bg-[#2db783] text-white hover:bg-[#249a6e]',
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  disabled = false,
  type = 'button',
  onClick,
  className = '',
}) {
  const base = 'inline-flex items-center justify-center gap-2 font-semibold rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-brand-purple/30'
  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-sm',
  }
  const width = fullWidth ? 'w-full' : ''
  const v = variants[variant] || variants.primary

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`${base} ${sizes[size]} ${v} ${width} ${className}`}
    >
      {children}
    </button>
  )
}
