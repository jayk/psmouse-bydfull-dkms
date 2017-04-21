/*
 * byd.h --- Driver for BYD Touchpad
 *
 * Copyright (C) 2015, Tai Chi Minh Ralph Eastwood
 * Copyright (C) 2015, Martin Wimpress
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 2 as published by
 * the Free Software Foundation.
 */

#ifndef __BYD_H
#define __BYD_H

#ifdef CONFIG_MOUSE_PS2_BYD

int byd_detect(struct psmouse *psmouse, bool set_properties);
int byd_init(struct psmouse *psmouse);

#define BYD_CMD_GESTURE				0
#define BYD_CMD_SCROLL_INC			1
#define BYD_CMD_SCROLL_DEC			-1
#define BYD_CMD_ABS_POS				2
#define BYD_CMD_ABS				2
#define BYD_RIGHT_CLICK_START_Y_POS		235
#define BYD_RIGHT_CLICK_START_X_POS		225

/* Flags from first byte of PS2 packet */
#define BTN_LEFT_BIT   0x01
#define BTN_RIGHT_BIT  0x02
#define BTN_MIDDLE_BIT 0x04
#define BTN_ANY_BIT    0x07
#define BTN_NONE_BIT   0x00

#else

static inline int byd_detect(struct psmouse *psmouse,
				      bool set_properties)
{
	return -ENOSYS;
}
static inline int byd_init(struct psmouse *psmouse)
{
	return -ENOSYS;
}

#endif /* CONFIG_MOUSE_PS2_BYD */

#endif /* !__BYD_H */
