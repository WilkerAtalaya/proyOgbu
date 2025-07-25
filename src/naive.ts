import { create, NMenu, NLayout, NButton } from 'naive-ui'

export default create({
  components: [NMenu, NLayout, NButton],
})
export const themeOverrides = {
    Menu: {
      itemTextColor: 'inherit',
      itemColorActive: 'transparent',
      itemColor: 'transparent',
      itemTextColorActive: '#000',
      itemBorderRadius: '0px',
      itemColorHover: 'transparent',
      itemHeight: '48px',
      itemPadding: '12px'
    }
  }
