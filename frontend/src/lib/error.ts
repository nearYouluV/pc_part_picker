type FastApiValidationDetail = {
    loc?: Array<string | number>;
    msg?: string;
    detail?: string;
};

export function getErrorMessage(error: any, fallback: string): string {
    const detail = error?.response?.data?.detail;

    if (typeof detail === 'string') {
        return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
        const parts = detail
            .map((item: FastApiValidationDetail) => {
                const field = item.loc?.[item.loc.length - 1];
                const label = typeof field === 'string' ? field : null;
                if (label && item.msg) {
                    return `${label}: ${item.msg}`;
                }
                return item.msg || item.detail || null;
            })
            .filter(Boolean);

        if (parts.length > 0) {
            return parts.join('\n');
        }
    }

    return fallback;
}