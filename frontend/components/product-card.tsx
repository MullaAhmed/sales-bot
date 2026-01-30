"use client";

import Image from "next/image";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface Variant {
  option: string;
  value: string;
  sku: string;
  price: number;
  image_url?: string;
}

interface Product {
  id: string;
  handle?: string;
  name: string;
  sku?: string;
  short_description?: string;
  description?: string;
  price: number | null;
  compare_at_price?: number | null;
  in_stock: boolean;
  image_url?: string;
  images?: string[];
  variants?: Variant[];
}

interface ProductCardProps {
  product: Product;
  compact?: boolean;
}

export function ProductCard({ product, compact = false }: ProductCardProps) {
  const [selectedVariant, setSelectedVariant] = useState<Variant | null>(null);
  const [imageError, setImageError] = useState(false);

  const currentPrice = selectedVariant?.price ?? product.price;
  const currentImage = selectedVariant?.image_url ?? product.image_url;
  const hasDiscount = product.compare_at_price && product.compare_at_price > (currentPrice ?? 0);
  const discountPercent = hasDiscount
    ? Math.round((1 - (currentPrice ?? 0) / product.compare_at_price!) * 100)
    : 0;

  if (compact) {
    return (
      <div className="flex gap-3 p-3 bg-muted/50 rounded-lg border border-border/50">
        {currentImage && !imageError ? (
          <div className="relative w-16 h-16 rounded-md overflow-hidden shrink-0 bg-muted">
            <Image
              src={currentImage}
              alt={product.name}
              fill
              className="object-cover"
              onError={() => setImageError(true)}
              sizes="64px"
            />
          </div>
        ) : (
          <div className="w-16 h-16 rounded-md bg-muted flex items-center justify-center shrink-0">
            <span className="text-2xl">📦</span>
          </div>
        )}
        <div className="flex flex-col justify-center min-w-0">
          <h4 className="font-medium text-sm truncate">{product.name}</h4>
          {currentPrice && (
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold">₹{currentPrice.toLocaleString("en-IN")}</span>
              {hasDiscount && (
                <span className="text-xs text-muted-foreground line-through">
                  ₹{product.compare_at_price!.toLocaleString("en-IN")}
                </span>
              )}
            </div>
          )}
          <span className={cn("text-xs", product.in_stock ? "text-green-600" : "text-red-500")}>
            {product.in_stock ? "In Stock" : "Out of Stock"}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden shadow-sm">
      {/* Image */}
      <div className="relative aspect-square bg-muted">
        {currentImage && !imageError ? (
          <Image
            src={currentImage}
            alt={product.name}
            fill
            className="object-cover"
            onError={() => setImageError(true)}
            sizes="(max-width: 768px) 100vw, 300px"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-6xl">📦</span>
          </div>
        )}
        {hasDiscount && (
          <div className="absolute top-2 left-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">
            {discountPercent}% OFF
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        <div>
          <h3 className="font-semibold text-base leading-tight">{product.name}</h3>
          {product.sku && (
            <p className="text-xs text-muted-foreground mt-0.5">SKU: {product.sku}</p>
          )}
        </div>

        {product.short_description && (
          <p className="text-sm text-muted-foreground line-clamp-2">
            {product.short_description}
          </p>
        )}

        {/* Price */}
        <div className="flex items-baseline gap-2">
          {currentPrice ? (
            <>
              <span className="text-xl font-bold">₹{currentPrice.toLocaleString("en-IN")}</span>
              {hasDiscount && (
                <span className="text-sm text-muted-foreground line-through">
                  ₹{product.compare_at_price!.toLocaleString("en-IN")}
                </span>
              )}
            </>
          ) : (
            <span className="text-lg text-muted-foreground">Price not available</span>
          )}
        </div>

        {/* Variants */}
        {product.variants && product.variants.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">
              {product.variants[0].option}:
            </p>
            <div className="flex flex-wrap gap-2">
              {product.variants.map((variant, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedVariant(
                    selectedVariant?.sku === variant.sku ? null : variant
                  )}
                  className={cn(
                    "px-3 py-1.5 text-xs rounded-full border transition-colors",
                    selectedVariant?.sku === variant.sku
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background border-border hover:border-primary/50"
                  )}
                >
                  {variant.value}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Stock Status */}
        <div className="flex items-center justify-between pt-2 border-t border-border/50">
          <span className={cn(
            "text-sm font-medium",
            product.in_stock ? "text-green-600" : "text-red-500"
          )}>
            {product.in_stock ? "✓ In Stock" : "✗ Out of Stock"}
          </span>
        </div>
      </div>
    </div>
  );
}

interface ProductListProps {
  products: Product[];
}

export function ProductList({ products }: ProductListProps) {
  if (products.length === 0) return null;

  if (products.length === 1) {
    return (
      <div className="max-w-xs">
        <ProductCard product={products[0]} />
      </div>
    );
  }

  if (products.length <= 3) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    );
  }

  // For many products, use compact view
  return (
    <div className="space-y-2">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} compact />
      ))}
    </div>
  );
}
